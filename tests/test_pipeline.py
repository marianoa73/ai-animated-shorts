import contextlib
import copy
import io
import json
import math
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import common
import qa_audio as qa
import check_inputs as ci
import voice
from pipeline import retry_loop
ROOT=common.ROOT
(ROOT/"cache").mkdir(exist_ok=True)

def wav(path,seconds=10,rate=24000,channels=1,amplitude=.5,width=2):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(channels);w.setsampwidth(width);w.setframerate(rate)
        frame=struct.pack('<h',round(amplitude*32767)) if width==2 else b'\x80'
        w.writeframes(frame*round(seconds*rate)*channels)

def png(path,width=1024,height=1024):
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
    raw=(b'\x00'+b'\x80\x90\xa0'*width)*height
    Path(path).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))

class ScriptTests(unittest.TestCase):
    def setUp(self):self.s=common.read(ROOT/'episodes/example/script.json')
    def test_example(self):self.assertGreater(common.validate_script(self.s),30)
    def test_last_closing(self):
        self.s['lines'][-1]['shot']='close'
        with self.assertRaises(ValueError):common.validate_script(self.s)
    def test_alternation(self):
        self.s['lines'][1]['who']=self.s['lines'][0]['who']
        with self.assertRaises(ValueError):common.validate_script(self.s)
    def test_say_keeps_text(self):
        l={'text':'ABC','say':'a be ce'};self.assertEqual(common.spoken(l),'a be ce');self.assertEqual(l['text'],'ABC')
    def test_bad_types(self):
        for k,v in [('subtitles','yes'),('width',721),('fps',24),('pause',.8),('characters',['../x','b'])]:
            with self.subTest(k=k):
                s=copy.deepcopy(self.s);s[k]=v
                with self.assertRaises(ValueError):common.validate_script(s)
    def test_short_rejected(self):
        self.s['lines']=self.s['lines'][:2];self.s['lines'][-1]['shot']='closing'
        with self.assertRaises(ValueError):common.validate_script(self.s)
        common.validate_script(self.s,short=True)
    def test_traversal(self):
        with self.assertRaises(ValueError):common.local('../outside')
    def test_seed_boolean(self):
        self.s['lines'][0]['seed']=True
        with self.assertRaises(ValueError):common.validate_script(self.s)
    def test_utf8_speech(self):self.assertEqual(qa.tokens('Árbol, ÉCOLE! 東京'),['arbol','ecole','東','京'])

class PhraseTests(unittest.TestCase):
    def test_last_short_regression(self):self.assertEqual(voice.phrases('Esta frase tiene palabras. Otra frase bastante larga. Sí.'),['Esta frase tiene palabras.','Otra frase bastante larga. Sí.'])
    def test_two_short_last(self):self.assertEqual(voice.phrases('Una oración bien completa. Fin.'),['Una oración bien completa. Fin.'])
    def test_first_short(self):self.assertEqual(voice.phrases('Hola. Esta es una frase.'),['Hola. Esta es una frase.'])
    def test_pipes(self):self.assertEqual(voice.phrases('Esta parte tiene palabras | Esta otra también tiene palabras'),['Esta parte tiene palabras','Esta otra también tiene palabras'])
    def test_empty(self):self.assertEqual(voice.phrases(' | '),[])
    def test_no_punctuation(self):self.assertEqual(voice.phrases('Una sola oración completa'),['Una sola oración completa'])
    def test_key_changes(self):
        base=voice.cache_key('hola',1,{'tempo':1},'sample')
        for args in [('otro',1,{'tempo':1},'sample'),('hola',2,{'tempo':1},'sample'),('hola',1,{'tempo':1.1},'sample'),('hola',1,{'tempo':1},'changed')]:self.assertNotEqual(base,voice.cache_key(*args))
    def test_phrase_separator_changes_key(self):self.assertNotEqual(voice.cache_key('uno | dos',1,{},'s'),voice.cache_key('uno   dos',1,{},'s'))
    def test_key_stable(self):self.assertEqual(voice.cache_key('x',1,{'a':2,'b':3},'s'),voice.cache_key('x',1,{'b':3,'a':2},'s'))

class QATests(unittest.TestCase):
    def setUp(self):
        self.sr=1000;self.text='Esta frase termina con claridad.'
        self.data=[.1*math.sin(i*.7) for i in range(2000)]+[0]*200
        words=self.text.split();self.words=[{'word':w,'start':i*.35,'end':(i+1)*.35+.2} for i,w in enumerate(words)]
    def review(self,**kw):return qa.review(kw.get('data',self.data),self.sr,kw.get('text',self.text),kw.get('words',self.words),kw.get('engine','chatterbox'))
    def test_clean(self):self.assertTrue(self.review()['ok'])
    def test_clipping(self):
        self.data[50]=1;self.assertIn('clipping',self.review()['failures'])
    def test_tail_absolute(self):
        self.data[-150:]=[.02]*150;self.assertIn('tail_not_silent',self.review()['failures'])
    def test_silence_inside(self):
        self.data[500:1200]=[0]*700;self.assertIn('internal_silence',self.review()['failures'])
    def test_leading_silence_not_internal(self):
        self.assertNotIn('internal_silence',self.review(data=[0]*700+self.data)['failures'])
    def test_late_tail(self):self.assertIn('tail_after_word',self.review(data=self.data+[0]*1000)['failures'])
    def test_last_word(self):self.assertIn('last_word_missing',self.review(words=self.words[:-1])['failures'])
    def test_missing_words(self):self.assertIn('words_below_90_percent',self.review(words=self.words[2:])['failures'])
    def test_rate(self):self.assertIn('speech_rate',self.review(text=self.text*5)['failures'])
    def test_fallback_is_failure(self):self.assertIn('fallback_voice',self.review(engine='piper')['failures'])
    def test_empty(self):self.assertFalse(self.review(data=[],words=[])['ok'])
    def test_cjk_tokenization(self):self.assertEqual(qa.tokens('你好 世界'),qa.tokens('你好世界'))
    def test_reordering_not_bag_of_words(self):self.assertLess(len(qa.align(['one','two','three'],['three','two','one'])),3)
    def test_fuzzy_lcs(self):self.assertEqual(qa.align(['color','house'],['colour','house']),[(0,0),(1,1)])
    def test_final_duration(self):self.assertIn('duration_not_over_30',qa.final_alignment([{'text':self.text}],self.words,30))
    def test_final_missing_line(self):self.assertIn('line_1_text',qa.final_alignment([{'text':self.text},{'text':'Una oración diferente'}],self.words,40))
    def test_final_gap(self):
        lines=[{'text':'Hola mundo'},{'text':'Todo bien'}];words=[{'word':w,'start':a,'end':b} for w,a,b in [('Hola',0,.3),('mundo',.3,.6),('Todo',2,2.3),('bien',2.3,2.6)]]
        self.assertIn('gap_after_0',qa.final_alignment(lines,words,40))
    def test_mock_whisper(self):
        from types import SimpleNamespace as N
        class Model:
            def transcribe(self,*args,**kwargs):return iter([N(words=[N(word='Hola',start=0,end=.3)])]),None
        self.assertEqual(qa.transcribe('unused','es',Model())[0]['word'],'Hola')
    def test_wav_roundtrip(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'cache') as d:
            p=Path(d)/'a.wav';wav(p,seconds=.1);samples,sr=qa.pcm(p);self.assertEqual(sr,24000);self.assertEqual(len(samples),2400)

class InputTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'cache');self.d=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def test_voice_valid(self):
        f=self.d/'ok.wav';wav(f);self.assertAlmostEqual(ci.check_voice(f)['peak_db'],-6.02,places=1)
    def test_voice_invalid(self):
        for n,opts in [('short',{'seconds':9}),('long',{'seconds':31}),('stereo',{'channels':2}),('rate',{'rate':16000}),('loud',{'amplitude':1}),('quiet',{'amplitude':.01}),('width',{'width':1})]:
            f=self.d/(n+'.wav');wav(f,**opts)
            with self.subTest(n=n),self.assertRaises(ValueError):ci.check_voice(f)
    def test_image_valid(self):
        f=self.d/'ok.png';png(f);self.assertEqual(ci.check_image(f)['width'],1024)
    def test_image_small(self):
        f=self.d/'bad.png';png(f,100,200)
        with self.assertRaises(ValueError):ci.check_image(f)
    def test_invalid_image(self):
        f=self.d/'bad.jpg';f.write_bytes(b'invalid')
        with self.assertRaises(ValueError):ci.check_image(f)
    def test_jpeg_header(self):
        f=self.d/'header.jpg';f.write_bytes(b'\xff\xd8\xff\xc0\x00\x08\x08'+struct.pack('>HH',1200,1300)+b'\x01')
        self.assertEqual(ci.image_size(f),(1300,1200))
    def test_character_valid(self):ci.check_character(common.read(ROOT/'characters/example-a.json'))
    def test_character_bad_color(self):
        c=common.read(ROOT/'characters/example-a.json');c['palette']['skin']='invalid'
        with self.assertRaises(ValueError):ci.check_character(c)
    def test_character_bad_proportion(self):
        c=common.read(ROOT/'characters/example-a.json');c['proportions']['headSize']=99
        with self.assertRaises(ValueError):ci.check_character(c)
    def test_missing_samples_stop(self):
        with patch.object(ci,'voice_config',side_effect=FileNotFoundError('missing reference')),self.assertRaises(FileNotFoundError):ci.check_all(common.read(ROOT/'episodes/example/script.json'))

class RetryTests(unittest.TestCase):
    def test_success_no_retries(self):
        calls=[];self.assertTrue(retry_loop(lambda i,a:calls.append((i,a)) or 0,lambda:0,lambda:[1]));self.assertEqual(calls,[(None,0)])
    def test_retry_only_bad(self):
        calls=[];results=iter([1,1,0]);self.assertTrue(retry_loop(lambda i,a:calls.append((i,a)) or 0,lambda:next(results),lambda:[2]));self.assertEqual(calls,[(None,0),([2],1),([2],2)])
    def test_five_retries_then_stop(self):
        calls=[];self.assertFalse(retry_loop(lambda i,a:calls.append(a) or 0,lambda:1,lambda:[0]));self.assertEqual(calls,list(range(6)))
    def test_no_report_stops(self):self.assertFalse(retry_loop(lambda i,a:0,lambda:1,lambda:[]))
    def test_generator_error_stops(self):self.assertFalse(retry_loop(lambda i,a:1,lambda:0,lambda:[]))

class VoiceMockTests(unittest.TestCase):
    def test_cache_reuse_and_selective_retry(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'cache') as d:
            root=Path(d);sample=root/'sample.wav';wav(sample);ep=root/'episodes/demo';ep.mkdir(parents=True)
            s={'lines':[{'who':'a','text':'Una frase para probar.'},{'who':'b','text':'Otra frase para probar.'}]}
            c={'tempo':1};calls=[]
            class Fake:
                def generate(self,text,seed,c,sample,path):calls.append((text,seed));wav(path,seconds=2)
            with patch.object(voice,'ROOT',root),patch.object(voice,'local',lambda p:root/p),patch.object(voice,'voice_config',lambda n:(c,sample)):
                first=voice.generate(ep,s,synth_factory=Fake);self.assertEqual(len(calls),2)
                voice.generate(ep,s,synth_factory=Fake);self.assertEqual(len(calls),2)
                second=voice.generate(ep,s,retry={1},attempt=1,synth_factory=Fake)
                self.assertEqual(len(calls),3);self.assertEqual(first[0],second[0]);self.assertNotEqual(first[1]['key'],second[1]['key'])


class StateTests(unittest.TestCase):
    def test_approval_requires_current_hash_and_visual_review(self):
        from status import set_status
        with tempfile.TemporaryDirectory(dir=ROOT/'cache') as d:
            root=Path(d);(root/'output').mkdir();v=root/'output/demo.mp4';v.write_bytes(b'fake video')
            common.save(root/'output/demo-qa.json',{'ok':True,'video_hash':common.file_hash(v)})
            with self.assertRaises(ValueError):set_status('demo','aprobados',False,root)
            self.assertEqual(set_status('demo','aprobados',True,root)['demo']['state'],'aprobados')
            v.write_bytes(b'changed video')
            with self.assertRaises(ValueError):set_status('demo','produccion',True,root)
    def test_failure_cannot_be_approved(self):
        from status import set_status
        with tempfile.TemporaryDirectory(dir=ROOT/'cache') as d:
            root=Path(d);(root/'output').mkdir();v=root/'output/demo.mp4';v.write_bytes(b'fake')
            common.save(root/'output/demo-qa.json',{'ok':False,'video_hash':common.file_hash(v)})
            with self.assertRaises(ValueError):set_status('demo','aprobados',True,root)
            self.assertEqual(set_status('demo','pruebas',False,root)['demo']['state'],'pruebas')
    def test_invalid_name(self):
        from status import set_status
        with self.assertRaises(ValueError):set_status('../secret','revision')

if __name__=='__main__':unittest.main()

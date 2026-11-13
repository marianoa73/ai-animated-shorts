#!/usr/bin/env python3
"""Rebuild five matching SVG/PNG diagrams. Pillow needed only for PNG output."""
from pathlib import Path
from html import escape
import math
from PIL import Image, ImageDraw, ImageFont
OUT=Path(__file__).resolve().parent
BG='#0F1115'; BOX='#202630'; FG='#EDF0F4'; MUTED='#BBC5D4'; ACCENT='#FD5A02'
class Diagram:
    def __init__(self,title,subtitle,h=840):
        self.w=1400;self.h=h;self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{h}" viewBox="0 0 1400 {h}" role="img"><title>{escape(title)}</title><rect width="1400" height="{h}" fill="{BG}"/>']
        self.im=Image.new('RGB',(1400,h),BG);self.d=ImageDraw.Draw(self.im)
        self.text(50,48,title,34,FG,True);self.text(50,95,subtitle,20,MUTED)
    def text(self,x,y,text,size=21,color=FG,bold=False,anchor='left'):
        font=ImageFont.truetype('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',size)
        self.d.text((x,y),text,font=font,fill=color,anchor='mm' if anchor=='middle' else 'lm')
        self.svg.append(f'<text x="{x}" y="{y}" dominant-baseline="middle" text-anchor="{"middle" if anchor=="middle" else "start"}" font-family="DejaVu Sans,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(text)}</text>')
    def box(self,x,y,w,h,title,lines=(),accent=False):
        stroke=ACCENT if accent else '#596778'
        self.d.rounded_rectangle((x,y,x+w,y+h),radius=16,fill=BOX,outline=stroke,width=3)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{BOX}" stroke="{stroke}" stroke-width="3"/>')
        start=y+h/2-(len(lines)*30)/2
        self.text(x+w/2,start,title,23,FG,True,'middle')
        for i,t in enumerate(lines):self.text(x+w/2,start+(i+1)*30,t,19,MUTED,False,'middle')
    def arrow(self,points,label=None):
        self.d.line(points,fill=ACCENT,width=4,joint='curve')
        x,y=points[-1];px,py=points[-2];a=math.atan2(y-py,x-px)
        triangle=[(x,y),(x-14*math.cos(a-.5),y-14*math.sin(a-.5)),(x-14*math.cos(a+.5),y-14*math.sin(a+.5))]
        self.d.polygon(triangle,fill=ACCENT)
        self.svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{ACCENT}" stroke-width="4"/>')
        self.svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in triangle)+f'" fill="{ACCENT}"/>')
        if label:self.text(*label,18,FG)
    def save(self,name):
        (OUT/(name+'.svg')).write_text(''.join(self.svg)+'</svg>\n')
        self.im.save(OUT/(name+'.png'))

def main():
    s=Diagram('01 · Del guion a la revisión','Procesamiento local · dos personajes configurables · publicación siempre manual')
    entries=[('Guion',['text + say','plano, gesto y semilla']),('Voces + caché',['Chatterbox CPU','muestras propias']),('Control por línea',['texto, ritmo y señal','hasta 5 reintentos']),('Render 3D',['three.js + Chromium','30 cuadros por segundo']),('Mezcla',['música + ducking','cortes + −15 LUFS']),('Control final',['alineación y duración','volumen + 4 cuadros']),('Revisión local',['estados en status.json','decisión de una persona']),('Publicación manual',['fuera del pipeline','derechos confirmados'])]
    for i,(title,lines) in enumerate(entries):
        col=i%4;row=i//4;s.box(50+col*335,190+row*300,290,145,title,lines,i==6)
        if col<3:s.arrow([(340+col*335,262+row*300),(385+col*335,262+row*300)])
    s.arrow([(1200,335),(1200,410),(195,410),(195,490)])
    s.arrow([(865,190),(865,145),(530,145),(530,190)])
    s.text(50,750,'Una falla detiene la aprobación; las muestras privadas no se sirven en la web.',23)
    s.save('01-flujo')
    s=Diagram('02 · Control de audio y corrección','La aprobación se basa en el audio generado, no en la promesa del modelo',950)
    s.box(50,160,420,180,'Analizar WAV',['≥ 90 % de palabras + última','cola < −45 dBFS / 150 ms','pico < −1 dBFS'],True)
    s.box(50,390,420,170,'Verificar tiempos',['silencio interno ≤ 0,6 s','cola tras palabra ≤ 0,6 s','ritmo 9–20 caracteres/s'])
    s.arrow([(260,340),(260,390)])
    s.box(560,390,310,170,'¿Cumple todo?',['Piper = falla','sin informe = falla'],True)
    s.arrow([(470,475),(560,475)])
    s.box(980,160,350,140,'Aprobar la línea',['guardar hash y control','reutilizar si nada cambia'])
    s.arrow([(715,390),(715,230),(980,230)],(760,205,'Sí'))
    s.box(980,390,350,170,'Aumentar seed',['regenerar sólo la fallida','máximo 5 reintentos'])
    s.arrow([(870,475),(980,475)],(895,445,'No'))
    s.arrow([(1155,390),(1155,350),(500,350),(500,250),(470,250)])
    s.box(820,690,510,140,'Si persiste: intervención humana',['reescribir say, mantener el subtítulo','volver a controlar antes de renderizar'],True)
    s.arrow([(1155,560),(1155,690)])
    s.text(50,875,'Control final: LCS difuso · sin huecos > 1 s · duración > 30 s · volumen · inspección visual.',21)
    s.save('02-logica-control')
    s=Diagram('03 · Hardware y red privada','La inferencia y el render no requieren servicios en la nube')
    s.box(50,180,630,360,'Mini PC · equipo de render',['Intel i5 · 4 núcleos · 32 GB','Ubuntu 24.04 · Docker · CPU x86_64','Voces + imágenes + modelos + caché','Contenedores de trabajo sin red','Las muestras NO salen de este equipo'],True)
    s.box(850,180,500,190,'Navegador de revisión',['acceso local o por LAN privada','sólo videos y metadatos de revisión'])
    s.arrow([(680,275),(850,275)],(705,242,'Salida'))
    s.box(850,480,500,180,'Raspberry Pi opcional',['4B · 8 GB · Debian','sólo salida de revisión','proxy inverso HTTPS opcional'])
    s.arrow([(680,480),(760,480),(760,570),(850,570)])
    s.arrow([(1100,480),(1100,370)])
    s.text(50,620,'LAN privada · sin direcciones ni equipos personales',23)
    s.text(50,710,'Descargar dependencias y pesos ANTES de aportar muestras.',23)
    s.text(50,755,'El material generado contiene voz: compartirlo también requiere consentimiento.',20,MUTED)
    s.save('03-hardware-red')
    s=Diagram('04 · Capas y versiones de referencia','Dependencias separadas del núcleo de pruebas sin modelos',880)
    layers=[('Orquestación','Docker Compose v2 · Python 3.11 (voces y QA)'),('Síntesis CPU','PyTorch 2.6 · Chatterbox multilingüe 0.1.7'),('Control de audio','faster-whisper 1.2 · CTranslate2 4.8 · modelo small'),('Escena y captura','Node · Playwright 1.49 · Chromium · three.js 0.170'),('Medios y respaldo','FFmpeg 6.1 · Piper 2023.11.14-2 (no aprueba QA)'),('Revisión','nginx 1.27 · HTML local · estados manuales')]
    for i,(title,line) in enumerate(layers):s.box(80,150+i*105,1240,85,title,[line],i in [1,2])
    s.text(80,820,'Pruebas unitarias: Python 3.13 · stdlib · sin modelos ni internet',22)
    s.save('04-herramientas')
    s=Diagram('05 · Estados de un video','Estados locales en status.json · no son órdenes de publicación')
    s.box(50,260,280,160,'Revisión',['todo video nuevo','o render actualizado'],True)
    s.box(520,160,320,150,'Pruebas',['ajustes y comparación','puede volver a Revisión'])
    s.box(520,470,320,150,'Aprobados',['control automático vigente','revisión visual explícita'],True)
    s.box(1010,470,330,150,'Producción',['selección manual','no sube a ninguna red'])
    s.arrow([(330,310),(420,310),(420,235),(520,235)])
    s.arrow([(330,370),(420,370),(420,545),(520,545)])
    s.arrow([(680,310),(680,470)])
    s.arrow([(840,545),(1010,545)])
    s.arrow([(1010,620),(1010,710),(190,710),(190,420)])
    s.text(360,750,'Nueva versión: invalida el control y vuelve a Revisión.',23)
    s.save('05-estados')
if __name__=='__main__':main()

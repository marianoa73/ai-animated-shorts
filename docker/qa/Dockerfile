FROM python:3.11-slim-bookworm AS ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl xz-utils ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /build
RUN curl -fSL https://ffmpeg.org/releases/ffmpeg-6.1.2.tar.xz | tar -xJ && cd ffmpeg-6.1.2 && ./configure --disable-doc --disable-debug --disable-x86asm --disable-shared --enable-static && make -j2 && make install
FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 libgomp1 git && rm -rf /var/lib/apt/lists/*
COPY --from=ffmpeg /usr/local/bin/ffmpeg /usr/local/bin/ffmpeg
COPY --from=ffmpeg /usr/local/bin/ffprobe /usr/local/bin/ffprobe
RUN pip install --no-cache-dir faster-whisper==1.2.0 ctranslate2==4.8.0 && pip check
WORKDIR /work

FROM mcr.microsoft.com/playwright:v1.49.1-noble
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg curl ca-certificates python3 python3-pil fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/piper && curl -fSL https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz | tar -xz -C /opt
WORKDIR /opt/renderer
RUN npm init -y && npm install --save-exact playwright-core@1.49.1 three@0.170.0
ENV NODE_PATH=/opt/renderer/node_modules PIPER=/opt/piper/piper
WORKDIR /work

# syntax=docker/dockerfile:1
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

# whisperx 会拉 torch 2.8 + CUDA 12.8，与服务器 GPU 兼容，无需从 cu124 源重装
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install whisperx

COPY . .

RUN mkdir -p uploads results

EXPOSE 9023
ENV PORT=9023
ENV APP_PASSWORD=1111iran
ENV HF_ENDPOINT=https://hf-mirror.com

CMD ["python3", "app.py"]

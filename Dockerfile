FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 先装 whisperx（拉 torch 2.8），再用 cu124 源重装 CUDA 版 torch
RUN pip3 install --no-cache-dir whisperx
RUN pip3 install --no-cache-dir --force-reinstall torch torchaudio --index-url https://download.pytorch.org/whl/cu124

COPY . .

RUN mkdir -p uploads results

EXPOSE 9023
ENV PORT=9023
ENV APP_PASSWORD=1111iran
ENV HF_ENDPOINT=https://hf-mirror.com

CMD ["python3", "app.py"]

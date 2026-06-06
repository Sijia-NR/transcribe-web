FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3-pip ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir torch==2.4.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
RUN pip3 install --no-cache-dir whisperx

COPY . .

RUN mkdir -p uploads results

EXPOSE 9023
ENV PORT=9023
ENV APP_PASSWORD=1111iran
ENV HF_ENDPOINT=https://hf-mirror.com

CMD ["python3.11", "app.py"]

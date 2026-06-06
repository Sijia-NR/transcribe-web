#!/bin/bash
# 部署脚本：更新代码并重建容器
set -e

# 创建 git bundle 传输
git bundle create /tmp/transcribe-web.bundle HEAD main
scp /tmp/transcribe-web.bundle transcribe-server:/tmp/

ssh transcribe-server '
set -e
cd /data1/allresearchProject/transcribe-web

# 拉取代码
git stash -q 2>/dev/null || true
git pull /tmp/transcribe-web.bundle main
rm -f /tmp/transcribe-web.bundle

# 确保数据目录存在
mkdir -p uploads results shares shares_meta hf_cache

# 重建容器
docker build -t transcribe-web .
docker stop transcribe-web 2>/dev/null || true
docker rm transcribe-web 2>/dev/null || true
docker run -d --name transcribe-web --restart=always \
    --gpus all \
    -p 9023:9023 \
    -v /data1/allresearchProject/transcribe-web/uploads:/app/uploads \
    -v /data1/allresearchProject/transcribe-web/results:/app/results \
    -v /data1/allresearchProject/transcribe-web/shares:/app/shares \
    -v /data1/allresearchProject/transcribe-web/shares_meta:/app/shares_meta \
    -v /data1/allresearchProject/transcribe-web/hf_cache:/root/.cache/huggingface \
    -e APP_PASSWORD=1111iran \
    -e HF_ENDPOINT=https://hf-mirror.com \
    transcribe-web
'

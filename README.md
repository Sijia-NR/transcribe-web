# 录音转写

基于讯飞录音文件转写大模型 API 的音频转写 Web 应用。支持上传音频文件，自动转写为文字，支持说话人分离、导出 TXT/Word。

## 功能

- 音频文件上传（支持 mp3/wav/m4a/ogg/flac/aac 等格式，最大 500MB）
- 自动转写为文字，支持中英 + 202 种方言
- 说话人分离（角色识别）
- 说话人名称自定义
- 导出 TXT / Word 文档
- 转写历史记录（浏览器本地存储）
- 密码登录保护

## 快速开始

### 环境要求

- Python 3.8+
- ffprobe（用于获取音频时长，可通过 ffmpeg 安装）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python app.py
```

默认端口 `9023`，访问 http://localhost:9023

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PORT` | 服务端口 | 9023 |
| `APP_PASSWORD` | 登录密码 | 1111iran |
| `SECRET_KEY` | Session 密钥 | 随机值（生产环境建议修改） |

## 使用说明

1. 访问服务地址，输入密码登录
2. 填写讯飞开放平台的认证信息（APP ID / API Key / API Secret）
3. 上传音频文件，等待转写完成
4. 查看结果、编辑说话人名称、导出文档

## 讯飞认证信息获取

1. 前往 [讯飞控制台](https://console.xfyun.cn/app/myapp) 创建应用
2. 开通 [录音文件转写](https://console.xfyun.cn/services/new_lfasr) 服务
3. 获取 APPID、APIKey、APISecret
4. 新用户可免费使用 5 小时转写额度

---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b0f711f0a87bffb247809f7d67924d56
    PropagateID: b0f711f0a87bffb247809f7d67924d56
    ReservedCode1: 304502206f5b1b8f4678ba0924f24848e5e439e1b94d99d696442ed3ef648d1af9cae5aa022100ae91fa4a23bafec8e7bebc2fad1240bd5ef0669ae1f1e3e2565df5e98c5a37f5
    ReservedCode2: 3045022037dff06e7a78f958c63f803d2148c8d82d67a0ff03a621a4869f6026bcffa50d022100cf23d9744d79c6784474db872925de4d2fad9cbcdeaf234d80e1babc2d5f8731
---

# MiniMax Streaming TTS API

基于 FastAPI 的 MiniMax 流式文字转语音 API 服务

## 功能特性

- 流式音频输出，减少等待时间
- 支持 200+ 种音色（中文、英文、日文、韩文等）
- 可调节语速、音量、语调
- 提供 Web UI 界面测试
- RESTful API 接口

## 快速开始

### 本地运行

**Linux/Mac:**
```bash
pip install -r requirements.txt
export MINIMAX_API_KEY=your_api_key
uvicorn app.main:app --reload
```

**Windows PowerShell:**
```powershell
pip install -r requirements.txt
$env:MINIMAX_API_KEY="your_api_key"
uvicorn app.main:app --reload
```

**Windows CMD:**
```cmd
pip install -r requirements.txt
set MINIMAX_API_KEY=your_api_key
uvicorn app.main:app --reload
```

### Docker 运行

**构建镜像：**
```bash
docker build -t streaming-tts-api .
```

**运行服务：**
```bash
# Linux/Mac
docker run -d -p 8000:8000 -e MINIMAX_API_KEY=your_api_key --name tts-api streaming-tts-api

# Windows PowerShell
docker run -d -p 8000:8000 -e MINIMAX_API_KEY=your_api_key --name tts-api streaming-tts-api
```

## API 接口

### 流式 TTS（GET）

```
GET /tts/stream?text=你好&voice=Chinese (Mandarin)_News_Anchor&speed=1.0
```

### 流式 TTS（POST）

```
POST /tts/stream
Content-Type: application/json

{
    "text": "你好，欢迎使用",
    "voice": "Chinese (Mandarin)_News_Anchor",
    "speed": 1.0,
    "volume": 1.0,
    "pitch": 0
}
```

### 获取音色列表

```
GET /voices
```

## 环境变量

| 变量 | 说明 | 必填 |
|------|------|------|
| MINIMAX_API_KEY | MiniMax API 密钥 | 是 |

## 部署

本项目已配置 Dockerfile，支持一键部署到容器环境。
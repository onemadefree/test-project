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

```bash
pip install -r requirements.txt
export MINIMAX_API_KEY=your_api_key
uvicorn app.main:app --reload
```

### Docker 运行

```bash
docker build -t streaming-tts-api .
docker run -p 8000:8000 -e MINIMAX_API_KEY=your_api_key streaming-tts-api
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
---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 075a8365597937259b251659092f766f
    PropagateID: 075a8365597937259b251659092f766f
    ReservedCode1: 3046022100b38e27bef8884e2aeda5c0599064b403077f029d20bc5ad05209b4e8049b1bbd02210095585a7916627a9171930550bf72e486ab0ef3da0f864d6ccf0d33a5baeff2f6
    ReservedCode2: 30450220133979a2b08a0aa551e830f92da62aff5555b9d6873fa5c8bdd7c7cc7777b65d022100f1e14770e9e254b8c9c544288624564c3963e182c9cf337e8a274216e148f647
---

# MiniMax Streaming TTS API

基于 FastAPI 的 MiniMax 流式文字转语音 API 服务

## ⚠️ 重要说明

**本程序仅支持 MiniMax 国内版（CN 版）Coding Plan，暂不支持国际版。**

- 国内版 API 地址：`https://api.minimaxi.com`
- 国际版 API 地址：`https://api.minimax.io`（不支持）

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

### 直接访问示例

直接在浏览器或命令行中访问即可获取音频文件：

```
http://localhost:8000/tts/stream?text=你好
http://localhost:8000/tts/stream?text=Hello&voice=English_expressive_narrator
```

### 命令行下载音频

```bash
# PowerShell
curl "http://localhost:8000/tts/stream?text=你好" -o output.mp3

# Linux/Mac
curl "http://localhost:8000/tts/stream?text=你好" -o output.mp3
```

### 流式 TTS（GET）

```
GET /tts/stream?text=你好&voice=female-shaonv-jingpin&speed=1.0
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
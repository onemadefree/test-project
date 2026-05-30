---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: fc4659875d64dc3df8501e41daf8f931
    PropagateID: fc4659875d64dc3df8501e41daf8f931
    ReservedCode1: 30440220784e54d8ec421ec3cb6434ff305ad9baa13c84817ec95ce95dc70d157945a4730220106b1d83ea69a378fcecb45d3e672815aad091de5bd5eea6d5d8cd19bddb4de0
    ReservedCode2: 3046022100e47578ef108b8e75688b0c50b1cb5ae548f32d0930a39e05405050859885c8cf02210095c8cd774c05945109d5e4d9c7986ce2fff41a7d882e3a9eceba28e94c15a5e7
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
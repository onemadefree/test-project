"""
MiniMax Streaming TTS API Service
基于 FastAPI 的流式文字转语音 API
"""

import os
import asyncio
import httpx
from typing import Optional, AsyncGenerator
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="MiniMax Streaming TTS API", version="1.0.0")

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "YOUR_API_KEY")
MINIMAX_API_BASE = "https://api.minimax.io"
TTS_ENDPOINT = "/v1/t2a_v2"


class TTSRequest(BaseModel):
    text: str
    voice: str = "Chinese (Mandarin)_News_Anchor"
    speed: float = 1.0
    volume: float = 1.0
    pitch: float = 0.0
    emotion: Optional[str] = None


async def stream_tts_audio(text: str, voice: str, speed: float = 1.0,
                          volume: float = 1.0, pitch: float = 0.0,
                          emotion: Optional[str] = None) -> AsyncGenerator[bytes, None]:
    """
    调用 MiniMax 流式 TTS API
    """
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "speech-01",
        "text": text,
        "voice_setting": {
            "voice_id": voice,
            "speed": speed,
            "volume": volume,
            "pitch": pitch
        },
        "audio_setting": {
            "audio_format": "mp3",
            "sample_rate": 32000
        }
    }

    if emotion:
        payload["voice_setting"]["emotion"] = emotion

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        try:
            async with client.stream(
                "POST",
                f"{MINIMAX_API_BASE}{TTS_ENDPOINT}",
                headers=headers,
                json=payload,
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"MiniMax API Error: {error_text}"
                    )

                async for chunk in response.aiter_bytes(chunk_size=8192):
                    if chunk:
                        yield chunk

        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to MiniMax API")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request to MiniMax API timed out")


@app.get("/")
async def root():
    """返回前端页面"""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")


@app.get("/voices")
async def list_voices():
    """返回可用音色列表"""
    return {
        "voices": [
            {"id": "Chinese (Mandarin)_News_Anchor", "name": "新闻主播", "language": "中文"},
            {"id": "Chinese (Mandarin)_Gentleman", "name": "绅士", "language": "中文"},
            {"id": "Chinese (Mandarin)_Sweet_Lady", "name": "甜美女士", "language": "中文"},
            {"id": "Chinese (Mandarin)_Warm_Girl", "name": "温暖女孩", "language": "中文"},
            {"id": "English_expressive_narrator", "name": "表情丰富 narrator", "language": "英文"},
            {"id": "English_radiant_girl", "name": "阳光女孩", "language": "英文"},
            {"id": "Japanese_CalmLady", "name": "冷静女士", "language": "日文"},
            {"id": "Korean_CalmGentleman", "name": "冷静绅士", "language": "韩文"},
        ]
    }


@app.post("/tts/stream")
async def tts_stream(request: TTSRequest):
    """
    流式 TTS 接口
    接收文本，返回流式音频
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(request.text) > 1000:
        raise HTTPException(status_code=400, detail="Text too long (max 1000 characters)")

    return StreamingResponse(
        stream_tts_audio(
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            volume=request.volume,
            pitch=request.pitch,
            emotion=request.emotion
        ),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline",
            "Transfer-Encoding": "chunked"
        }
    )


@app.get("/tts/stream")
async def tts_stream_get(
    text: str = Query(..., description="要转换的文本"),
    voice: str = Query("Chinese (Mandarin)_News_Anchor", description="音色ID"),
    speed: float = Query(1.0, ge=0.5, le=2.0, description="语速"),
    volume: float = Query(1.0, ge=0, le=2.0, description="音量"),
    pitch: float = Query(0, ge=-12, le=12, description="语调")
):
    """
    GET 方式的流式 TTS 接口
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="Text too long (max 1000 characters)")

    return StreamingResponse(
        stream_tts_audio(
            text=text,
            voice=voice,
            speed=speed,
            volume=volume,
            pitch=pitch,
            emotion=None
        ),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline",
            "Transfer-Encoding": "chunked"
        }
    )


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "MiniMax Streaming TTS API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
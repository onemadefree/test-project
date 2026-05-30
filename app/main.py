"""
MiniMax Streaming TTS API Service
基于 FastAPI 的流式文字转语音 API
"""

import os
import binascii
import httpx
import json
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

app = FastAPI(title="MiniMax Streaming TTS API", version="1.0.0")

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "YOUR_API_KEY")
MINIMAX_API_BASE = "https://api.minimaxi.com"  # 正确国内服务地址
TTS_ENDPOINT = "/v1/t2a_v2"


class TTSRequest(BaseModel):
    text: str
    voice: str = "female-shaonv-jingpin"
    speed: float = 1.0
    volume: float = 1.0
    pitch: float = 0.0
    emotion: Optional[str] = None


def generate_tts_audio(text: str, voice: str, speed: float = 1.0,
                       volume: float = 1.0, pitch: float = 0.0,
                       emotion: Optional[str] = None) -> bytes:
    """
    调用 MiniMax TTS API，返回完整音频数据
    """
    api_key = os.getenv("MINIMAX_API_KEY", "YOUR_API_KEY")

    # 处理 API Key 前缀
    if api_key.startswith("sk-cp-"):
        actual_key = api_key
    else:
        actual_key = f"sk-cp-{api_key}"

    headers = {
        "Authorization": f"Bearer {actual_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "speech-2.8-hd",
        "text": text,
        "stream": True,
        "voice_setting": {
            "voice_id": voice,
            "speed": float(speed),
            "vol": float(volume),
            "pitch": int(pitch)
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        },
        "output_format": "hex"
    }

    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{MINIMAX_API_BASE}{TTS_ENDPOINT}",
            headers=headers,
            json=payload,
            timeout=60.0
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"MiniMax API Error: {response.text}"
            )

        # 解析 SSE 格式的响应
        # 只保留最后一个包含实际音频数据的块，避免重复播放
        last_audio_chunk = b""
        for line in response.text.split('\n'):
            line = line.strip()
            if line.startswith("data: "):
                data_str = line[6:]
                try:
                    data_obj = json.loads(data_str)
                    if data_obj.get("data") and isinstance(data_obj["data"], dict):
                        audio_data = data_obj["data"]
                        if audio_data.get("audio") and audio_data["audio"]:
                            hex_data = audio_data["audio"]
                            if hex_data:
                                audio_bytes = binascii.unhexlify(hex_data)
                                if audio_bytes:
                                    last_audio_chunk = audio_bytes
                except (json.JSONDecodeError, ValueError, TypeError):
                    continue

        if not last_audio_chunk:
            # 获取详细的错误信息
            error_detail = "No audio data received"
            for line in response.text.split('\n'):
                line = line.strip()
                if line.startswith("data: ") and '"status_code"' in line:
                    try:
                        data_obj = json.loads(line[6:])
                        if data_obj.get("base_resp"):
                            error_detail = f"API Error {data_obj['base_resp'].get('status_code')}: {data_obj['base_resp'].get('status_msg', 'Unknown')}"
                    except:
                        pass
            raise HTTPException(status_code=500, detail=error_detail)

        return last_audio_chunk


@app.get("/")
async def root():
    """返回前端页面"""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")


@app.get("/voices")
async def list_voices():
    """返回可用音色列表（基于 MiniMax 国内版 API）"""
    return {
        "voices": [
            # v1 基础音色
            {"id": "male-qn-qingse", "name": "青涩青年", "language": "中文", "version": "v1"},
            {"id": "male-qn-jingying", "name": "精英青年", "language": "中文", "version": "v1"},
            {"id": "male-qn-badao", "name": "霸道青年", "language": "中文", "version": "v1"},
            {"id": "male-qn-daxuesheng", "name": "青年大学生", "language": "中文", "version": "v1"},
            {"id": "female-shaonv", "name": "少女", "language": "中文", "version": "v1"},
            {"id": "female-yujie", "name": "御姐", "language": "中文", "version": "v1"},
            {"id": "female-chengshu", "name": "成熟女性", "language": "中文", "version": "v1"},
            {"id": "female-tianmei", "name": "甜美女性", "language": "中文", "version": "v1"},
            # v1 精选音色（Beta）
            {"id": "male-qn-qingse-jingpin", "name": "青涩青年-精选", "language": "中文", "version": "v1"},
            {"id": "male-qn-jingying-jingpin", "name": "精英青年-精选", "language": "中文", "version": "v1"},
            {"id": "male-qn-badao-jingpin", "name": "霸道青年-精选", "language": "中文", "version": "v1"},
            {"id": "male-qn-daxuesheng-jingpin", "name": "青年大学生-精选", "language": "中文", "version": "v1"},
            {"id": "female-shaonv-jingpin", "name": "少女-精选", "language": "中文", "version": "v1"},
            {"id": "female-yujie-jingpin", "name": "御姐-精选", "language": "中文", "version": "v1"},
            {"id": "female-chengshu-jingpin", "name": "成熟女性-精选", "language": "中文", "version": "v1"},
            {"id": "female-tianmei-jingpin", "name": "甜美女性-精选", "language": "中文", "version": "v1"},
            # v2 音色
            {"id": "clever_boy", "name": "聪明男童", "language": "中文", "version": "v2"},
            {"id": "cute_boy", "name": "可爱男童", "language": "中文", "version": "v2"},
            {"id": "lovely_girl", "name": "萌萌女童", "language": "中文", "version": "v2"},
            {"id": "badao_shaoye", "name": "霸道少爷", "language": "中文", "version": "v2"},
            {"id": "tianxin_xiaoling", "name": "甜心小玲", "language": "中文", "version": "v2"},
            {"id": "wumei_yujie", "name": "妩媚御姐", "language": "中文", "version": "v2"},
            # 英文音色
            {"id": "English_expressive_narrator", "name": "英文 Narrator", "language": "英文", "version": "v2"},
            {"id": "Sweet_Girl", "name": "Sweet Girl", "language": "英文", "version": "v2"},
            {"id": "Charming_Santa", "name": "Charming Santa", "language": "英文", "version": "v2"},
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

    try:
        audio_data = generate_tts_audio(
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            volume=request.volume,
            pitch=request.pitch,
            emotion=request.emotion
        )
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline",
                "Content-Length": str(len(audio_data))
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tts/stream")
async def tts_stream_get(
    text: str = Query(..., description="要转换的文本"),
    voice: str = Query("female-shaonv-jingpin", description="音色ID"),
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

    try:
        audio_data = generate_tts_audio(
            text=text,
            voice=voice,
            speed=speed,
            volume=volume,
            pitch=pitch,
            emotion=None
        )
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline",
                "Content-Length": str(len(audio_data))
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "MiniMax Streaming TTS API",
        "api_key_set": bool(os.getenv("MINIMAX_API_KEY") and os.getenv("MINIMAX_API_KEY") != "YOUR_API_KEY")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
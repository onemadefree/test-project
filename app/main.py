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

# 音色配置路径
VOICES_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "voices.json")


def load_voices():
    """从配置文件加载音色列表"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "voices.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("system_voice", [])
    except Exception as e:
        print(f"Warning: Failed to load voices config: {e}")
        return []


class TTSRequest(BaseModel):
    text: str
    voice: str = "female-shaonv-jingpin"
    speed: float = 1.0
    volume: float = 1.0
    pitch: float = 0.0
    emotion: Optional[str] = None
    model: str = "speech-2.8-hd"
    audio_format: str = "mp3"
    sample_rate: int = 32000
    bitrate: int = 128000
    channel: int = 1
    stream: bool = True
    voice_id: Optional[str] = None  # 自定义音色ID


def generate_tts_audio(text: str, voice: str, speed: float = 1.0,
                       volume: float = 1.0, pitch: float = 0.0,
                       emotion: Optional[str] = None,
                       model: str = "speech-2.8-hd",
                       audio_format: str = "mp3",
                       sample_rate: int = 32000,
                       bitrate: int = 128000,
                       channel: int = 1,
                       stream: bool = True,
                       custom_voice_id: Optional[str] = None) -> bytes:
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

    # 构建音色设置
    voice_id = custom_voice_id if custom_voice_id else voice

    payload = {
        "model": model,
        "text": text,
        "stream": stream,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": float(speed),
            "vol": float(volume),
            "pitch": int(pitch)
        },
        "audio_setting": {
            "sample_rate": sample_rate,
            "bitrate": bitrate,
            "format": audio_format,
            "channel": channel
        },
        "pronunciation_dict": {
            "tone": []
        },
        "output_format": "hex"
    }

    # 添加情绪参数（如果有）
    if emotion and emotion != "auto":
        payload["voice_setting"]["emotion"] = emotion

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
    """返回可用音色列表（从配置文件加载）"""
    voices_data = load_voices()

    if not voices_data:
        # 如果配置文件加载失败，返回简化列表
        return {
            "voices": [
                {"id": "female-shaonv-jingpin", "name": "少女音色-beta", "language": "中文", "description": ""},
                {"id": "male-qn-qingse-jingpin", "name": "青涩青年音色-beta", "language": "中文", "description": ""},
            ]
        }

    # 格式化返回
    formatted_voices = []
    for v in voices_data:
        formatted_voices.append({
            "id": v.get("voice_id", ""),
            "name": v.get("name", ""),
            "language": v.get("language", "未知"),
            "description": v.get("description", "")
        })

    return {"voices": formatted_voices, "total": len(formatted_voices)}


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
            emotion=request.emotion,
            model=request.model,
            audio_format=request.audio_format,
            sample_rate=request.sample_rate,
            bitrate=request.bitrate,
            channel=request.channel,
            stream=request.stream,
            custom_voice_id=request.voice_id
        )

        # 根据音频格式确定 media_type
        if request.audio_format == "wav":
            media_type = "audio/wav"
        elif request.audio_format == "pcm":
            media_type = "audio/pcm"
        else:
            media_type = "audio/mpeg"

        return StreamingResponse(
            iter([audio_data]),
            media_type=media_type,
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
    pitch: float = Query(0, ge=-12, le=12, description="语调"),
    emotion: str = Query(None, description="情绪: auto/happy/sad/angry/fear/disgust/surprise/neutral"),
    model: str = Query("speech-2.8-hd", description="模型选择"),
    audio_format: str = Query("mp3", description="音频格式: mp3/wav/pcm"),
    sample_rate: int = Query(32000, description="采样率"),
    bitrate: int = Query(128000, description="比特率"),
    channel: int = Query(1, ge=1, le=2, description="声道: 1单声道/2双声道"),
    custom_voice_id: str = Query(None, description="自定义音色ID")
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
            emotion=emotion,
            model=model,
            audio_format=audio_format,
            sample_rate=sample_rate,
            bitrate=bitrate,
            channel=channel,
            stream=True,
            custom_voice_id=custom_voice_id
        )

        # 根据音频格式确定 media_type
        if audio_format == "wav":
            media_type = "audio/wav"
        elif audio_format == "pcm":
            media_type = "audio/pcm"
        else:
            media_type = "audio/mpeg"

        return StreamingResponse(
            iter([audio_data]),
            media_type=media_type,
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
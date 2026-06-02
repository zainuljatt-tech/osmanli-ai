from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import Response
from app.core.dependencies import get_current_user
from app.models.user import User
from app.voice.speech_service import speech_service

router = APIRouter()


@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    audio_data = await file.read()
    result = await speech_service.speech_to_text(audio_data, file.filename or "audio.wav")
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result.get("error"))
    return result


@router.post("/tts")
async def text_to_speech(text: str = Form(...), voice: str = Form("alloy"), current_user: User = Depends(get_current_user)):
    audio_data = await speech_service.text_to_speech(text, voice)
    if not audio_data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="TTS failed")
    return Response(content=audio_data, media_type="audio/mpeg")


@router.get("/voices")
async def get_voices():
    return {"voices": await speech_service.get_available_voices()}

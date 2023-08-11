from fastapi import APIRouter, HTTPException
from llm_api.app.core.yandex_cloud_service import YandexCloudService
from llm_api.app.models.schemas.audio import AudioTaskCreate, AudioTaskResponse

router = APIRouter()
yandex_cloud_service = YandexCloudService()


@router.post("/tts/sync/")
async def tts_sync(audio_sync_task: AudioTaskCreate) -> AudioTaskResponse:
    try:
        text_from_audio = yandex_cloud_service.get_text_from_speech_sync(
            audio_sync_task.voice_message_url
        )
        return AudioTaskResponse(text=text_from_audio)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        raise HTTPException(500, detail=error_message) from e

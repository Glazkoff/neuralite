from fastapi import APIRouter, HTTPException
from llm_api.app.core.yandex_cloud_service import YandexCloudService
from llm_api.app.core.storage_service import StorageService
from llm_api.app.models.schemas.audio import (
    AudioTaskCreate,
    AudioTaskResponse,
)

router = APIRouter()
yandex_cloud_service = YandexCloudService()
storage_service = StorageService()


@router.post("/stt/sync/")
async def stt_sync(audio_sync_task: AudioTaskCreate) -> AudioTaskResponse:
    try:
        text_from_audio = yandex_cloud_service.get_text_from_speech_sync(
            audio_sync_task.file_url
        )
        return AudioTaskResponse(text=text_from_audio)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        raise HTTPException(500, detail=error_message) from e

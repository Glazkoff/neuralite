from fastapi import APIRouter, HTTPException
from llm_api.app.core.speech_to_text_service import SpeechToTextService
from llm_api.app.core.storage_service import StorageService
from llm_api.app.models.schemas.audio import (
    AudioTaskCreate,
    AudioTaskResponse,
    AudioTaskAsyncCreate,
    AudioTaskAsyncResponse,
    AudioTaskAsyncResults,
)

router = APIRouter()
yandex_cloud_service = SpeechToTextService()
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


@router.post("/stt/async/")
async def stt_async_start(
    audio_async_task: AudioTaskAsyncCreate,
) -> AudioTaskAsyncResponse:
    try:
        operation_id = yandex_cloud_service.start_async_stt(audio_async_task.S3_path)
        if operation_id is None:
            raise ValueError("Operations was not created")
        return AudioTaskAsyncResponse(operation_id=operation_id)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        raise HTTPException(500, detail=error_message) from e


@router.get("/stt/async/{operation_id}")
async def stt_async_start(
    operation_id: str,
) -> AudioTaskAsyncResults:
    try:
        done, text = yandex_cloud_service.get_result_async_stt(
            operation_id=operation_id
        )
        if done is None:
            raise ValueError("Check was failed")
        return AudioTaskAsyncResults(done=done, text=text)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        raise HTTPException(500, detail=error_message) from e

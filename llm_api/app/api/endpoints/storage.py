from fastapi import APIRouter, UploadFile, HTTPException
from llm_api.app.core.storage_service import StorageService
from llm_api.app.models.schemas.storage import (
    FileUploadCreate,
    FileUploadResponse,
)

router = APIRouter()
storage_service = StorageService()


@router.post("/upload/{key}")
async def upload_file(key: str, file: UploadFile):
    try:
        file_object = file.file
        file_key = storage_service.upload_file(file=file_object, key=key)
        return {"file_key": file_key}
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        raise HTTPException(500, detail=error_message) from e


@router.post("/upload/from_url/")
async def stt_sync(audio_sync_task: FileUploadCreate) -> FileUploadResponse:
    try:
        key = storage_service.upload_from_url(
            audio_sync_task.file_url, audio_sync_task.key
        )
        if key is None:
            raise ValueError("Problem with S3 upload")
        path = f"{storage_service.bucket}/{key}"
        return FileUploadResponse(path=path)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        raise HTTPException(500, detail=error_message) from e

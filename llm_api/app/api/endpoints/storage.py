from fastapi import APIRouter, UploadFile, HTTPException
from llm_api.app.core.storage_service import StorageService

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

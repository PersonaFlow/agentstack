import os
import orjson
from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File, Query, Form, Body
import uuid
import structlog
from app.repositories.file import get_files_repository, FileRepository
# from app.repositories.api_key import get_api_key_repository, ApiKeyRepository
from app.schema.file import FileSchema, UploadFileSchema
from app.api.annotations import ApiKey
from app.core.configuration import settings
from typing import Optional
from app.utils.file_helpers import guess_mime_type

router = APIRouter()
DEFAULT_TAG = "Files"
logger = structlog.get_logger()

@router.post("", tags=[DEFAULT_TAG], response_model=FileSchema, status_code=status.HTTP_201_CREATED,
             operation_id="upload_file",
             summary="Upload a file",
             description="Uploads a file that can be used across various endpoints. <br> NOTE: MUST INCLUDE `user_id`")
async def upload_file(
    api_key: ApiKey,
    file: UploadFile = File(...),
    purpose: str = Form(...),
    user_id: str = Form(...),
    filename: Optional[str] = Form(None),
    kwargs: Optional[str] = Form(None),
    files_repository: FileRepository = Depends(get_files_repository),
    # api_key_repository: ApiKeyRepository = Depends(get_api_key_repository)
) -> FileSchema:
    try:
        # if user_id is None:
        #     user_id = await api_key_repository.find_api_user(api_key)
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_UPLOAD_SIZE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds the maximum allowed size.")
        data = UploadFileSchema(purpose=purpose, user_id=user_id, filename=filename, kwargs=kwargs)
        file_data = data.model_dump()
        file_data["bytes"] = len(file_content)
        kwargs_dict = orjson.loads(kwargs) if kwargs else {}
        file_data["kwargs"] = kwargs_dict
        # Extract the file extension from the original filename
        _, file_extension = os.path.splitext(file.filename)
        file_extension = file_extension[1:]  # Remove the leading dot

        # Detect the MIME type using python-magic
        mime_type = guess_mime_type(file_content)

        file_data["mime_type"] = mime_type

        file_obj = await files_repository.create_file(data=file_data, file_content=file_content, file_extension=file_extension)
        return file_obj
    except Exception as e:
        await logger.exception(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while uploading the file.")

@router.get("", tags=[DEFAULT_TAG], response_model=list[FileSchema],
            operation_id="retrieve_files_for_user",
            summary="Retrieve files",
            description="Retrieves a list of files.")
async def retrieve_files(
    api_key: ApiKey,
    user_id: str = Query(...),
    purpose: Optional[str] = Query(None),
    files_repository: FileRepository = Depends(get_files_repository),
    # api_key_repository: ApiKeyRepository = Depends(get_api_key_repository)
) -> list[FileSchema]:
    # user_id = await api_key_repository.find_api_user(api_key)
    files = await files_repository.retrieve_files(user_id=user_id, purpose=purpose)
    return files

@router.get("/{file_id}", tags=[DEFAULT_TAG], response_model=FileSchema,
            operation_id="retrieve_file",
            summary="Retrieve a specific file",
            description="Retrieves information about a specific file by its ID.")
async def retrieve_file(
    api_key: ApiKey,
    file_id: uuid.UUID,
    files_repository: FileRepository = Depends(get_files_repository)
) -> FileSchema:
    file = await files_repository.retrieve_file(file_id=file_id)
    if file:
        return file
    raise HTTPException(status_code=404, detail="File not found")

@router.delete("/{file_id}", tags=[DEFAULT_TAG], status_code=status.HTTP_204_NO_CONTENT,
               operation_id="delete_file",
               summary="Delete a specific file",
               description="Deletes a specific file by its ID.")
async def delete_file(
    api_key: ApiKey,
    file_id: uuid.UUID,
    files_repository: FileRepository = Depends(get_files_repository)
):
    await files_repository.delete_file(file_id=file_id)
    return {"detail": "File deleted successfully"}

@router.get("/{file_id}/content", tags=[DEFAULT_TAG],
            operation_id="retrieve_file_content",
            summary="Retrieve the content of a specific file",
            description="Retrieves the content of a specific file by its ID.")
async def retrieve_file_content(
    api_key: ApiKey,
    file_id: uuid.UUID,
    files_repository: FileRepository = Depends(get_files_repository)
):
    file_content = await files_repository.retrieve_file_content(file_id=file_id)
    if file_content:
        return file_content
    raise HTTPException(status_code=404, detail="File content not found")

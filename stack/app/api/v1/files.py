import os
import orjson
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
    Request
)
import uuid
from stack.app.repositories.file import get_file_repository, FileRepository

from stack.app.core.auth.utils import get_header_user_id
from stack.app.schema.file import (
    FileSchema,
    UploadFileSchema,
    DeleteFileResponse,
    FilePurpose,
)
from stack.app.core.auth.request_validators import AuthenticatedUser
from stack.app.core.configuration import settings
from typing import Optional
from stack.app.core.logger import logging
from stack.app.utils.file_helpers import (
    guess_mime_type,
    is_mime_type_supported,
    guess_file_extension,
)
from stack.app.vectordbs.qdrant import QdrantService
from stack.app.repositories.assistant import (
    get_assistant_repository,
    AssistantRepository,
)

router = APIRouter()
DEFAULT_TAG = "Files"
logger = logging.getLogger(__name__)


@router.post(
    "",
    tags=[DEFAULT_TAG],
    response_model=FileSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id="upload_file",
    summary="Upload a file",
    description="Uploads a file that can be used across various endpoints. <br> NOTE: MUST INCLUDE `user_id`",
)
async def upload_file(
    auth: AuthenticatedUser,
    request: Request,
    file: UploadFile = File(..., description="The file to upload."),
    purpose: str = Form(
        ...,
        description="The purpose of the file: 'assistants', 'threads', or 'personas'.",
    ),
    filename: Optional[str] = Form(
        None, description="The preferred name for the file."
    ),
    kwargs: Optional[str] = Form(
        None,
        description="Any additonal metadata to include for this file. This should be a JSON string.",
    ),
    files_repository: FileRepository = Depends(get_file_repository),
) -> FileSchema:
    try:
        if not file or not file.file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File is required."
            )
        user_id = get_header_user_id(request)
        
        file_content = await file.read()
        mime_type = guess_mime_type(file_content)
        if not is_mime_type_supported(mime_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type."
            )
        if len(file_content) > settings.MAX_FILE_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds the maximum allowed size.",
            )

        data = UploadFileSchema(
            purpose=purpose, user_id=user_id, filename=filename, kwargs=kwargs
        )
        file_data = data.model_dump()
        file_data["bytes"] = len(file_content)
        kwargs_dict = orjson.loads(kwargs) if kwargs else {}
        file_data["kwargs"] = kwargs_dict
        file_data["mime_type"] = mime_type

        file_obj = await files_repository.create_file(
            data=file_data, file_content=file_content
        )
        return file_obj
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading the file.",
        )


@router.get(
    "",
    tags=[DEFAULT_TAG],
    response_model=list[FileSchema],
    operation_id="retrieve_files_for_user",
    summary="Retrieve files",
    description="Retrieves a list of files.",
)
async def retrieve_files(
    auth: AuthenticatedUser,
    request: Request,
    purpose: Optional[str] = Query(None),
    files_repository: FileRepository = Depends(get_file_repository),
) -> list[FileSchema]:
    user_id = get_header_user_id(request)
    try:
        files = await files_repository.retrieve_files(user_id=user_id, purpose=purpose)
        return files
    except Exception as e:
        logger.error(f"Error retrieving files: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the files.",
        )


@router.get(
    "/{file_id}",
    tags=[DEFAULT_TAG],
    response_model=FileSchema,
    operation_id="retrieve_file",
    summary="Retrieve file information",
    description="Retrieves information about a specific file by its ID.",
)
async def retrieve_file(
    auth: AuthenticatedUser,
    request: Request,
    file_id: uuid.UUID,
    files_repository: FileRepository = Depends(get_file_repository),
) -> FileSchema:
    try:
        file = await files_repository.retrieve_file(file_id=file_id)
        if not file:
            logger.error(f"File not found for file id: {file_id}")
            raise HTTPException(status_code=404, detail="File not found")
        return file
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the file.",
        )


@router.delete(
    "/{file_id}",
    tags=[DEFAULT_TAG],
    response_model=DeleteFileResponse,
    operation_id="delete_file",
    summary="Delete a specific file",
    description="Deletes a specific file by its ID from the database and file system. When a file is deleted, it is also removed from any assistants that may be using it and all associated embeddings are deleted from the vector store.",
)
async def delete_file(
    auth: AuthenticatedUser,
    request: Request,
    file_id: uuid.UUID,
    files_repository: FileRepository = Depends(get_file_repository),
    assistant_repository: AssistantRepository = Depends(get_assistant_repository),
):
    user_id = get_header_user_id(request)
    try:
        file: FileSchema = await files_repository.retrieve_file(file_id=file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        if file.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        if file.purpose in [
            FilePurpose.ASSISTANTS,
            FilePurpose.THREADS,
            FilePurpose.RAG,
        ]:
            # delete any embeddings associated with the file from the vector db
            service = QdrantService()
            deleted_chunks = await service.delete(str(file_id))
            # If this is an assistants file, delete the file from any assistants that may be using it
            assistants = await assistant_repository.remove_all_file_references(file_id)
            num_of_assistants = len(assistants)
            logger.info(f"Deleted file from {num_of_assistants} assistants")
        else:
            deleted_chunks = []
            num_of_assistants = 0

        # delete the file from the filesystem
        ext = guess_file_extension(file.mime_type)
        file_path = f"{settings.FILE_DATA_DIRECTORY}/{file.id}.{ext}"

        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            logger.error(f"File not found on filesystem: {file_path}", exc_info=True)
        # delete the file from the database
        await files_repository.delete_file(file_id=file_id)

        return DeleteFileResponse(
            file_id=file_id,
            num_of_assistants=num_of_assistants,
            deleted_chunks=deleted_chunks,
            assistants=assistants,
        )
    except Exception as e:
        logger.error(f"Error deleting assistant file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting the file from the system.",
        )


@router.get(
    "/{file_id}/content",
    tags=[DEFAULT_TAG],
    operation_id="retrieve_file_content",
    summary="Retrieve the content of a specific file",
    description="Retrieves the content of a specific file by its ID. Returns a downloadable file.",
)
async def retrieve_file_content(
    auth: AuthenticatedUser,
    request: Request,
    file_id: uuid.UUID,
    files_repository: FileRepository = Depends(get_file_repository),
):
    try:
        return await files_repository.retrieve_file_content_as_response(str(file_id))
    except Exception as e:
        logger.error(f"Error retrieving file content: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An server error occurred while retrieving the file content.",
        )

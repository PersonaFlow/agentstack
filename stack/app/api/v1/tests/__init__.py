from fastapi import APIRouter, Response

# from stack.app.api.v1 import feedback
# from stack.app.api.v1 import chat
from stack.app.api.v1 import runs
from stack.app.api.v1 import users
from stack.app.api.v1 import threads
from stack.app.api.v1 import messages
from stack.app.api.v1 import assistants
from stack.app.api.v1 import rag
from stack.app.api.v1 import files

api_router = APIRouter()
# api_router.include_router(feedback.router, tags=["Feedback"])
# api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(runs.router, prefix="/runs")
api_router.include_router(users.router, prefix="/users")
api_router.include_router(threads.router, prefix="/threads")
api_router.include_router(messages.router, prefix="/messages")
api_router.include_router(assistants.router, prefix="/assistants")
api_router.include_router(rag.router, prefix="/rag")
api_router.include_router(files.router, prefix="/files")


@api_router.get("/health_check", tags=["Health Check"])
def health_check():
    return Response(content="OK", status_code=200)

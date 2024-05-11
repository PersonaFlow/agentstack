from fastapi import APIRouter, Request

from pyserver.app.core.configuration import Settings

settings = Settings()
if settings.ENABLE_LANGSMITH_TRACING:
    from langsmith import Client
    from pyserver.app.utils import aget_trace_url

    client = Client()

router = APIRouter()


@router.post("/feedback")
async def send_feedback(request: Request):
    data = await request.json()
    run_id = data.get("run_id")
    if run_id is None:
        return {
            "result": "No LangSmith run ID provided",
            "code": 400,
        }
    key = data.get("key", "user_score")
    vals = {**data, "key": key}
    if settings.ENABLE_LANGSMITH_TRACING:
        client.create_feedback(**vals)
    # TODO: add langfuse feedback
    return {"result": "posted feedback successfully", "code": 200}


@router.patch("/feedback")
async def update_feedback(request: Request):
    data = await request.json()
    feedback_id = data.get("feedback_id")
    if feedback_id is None:
        return {
            "result": "No feedback ID provided",
            "code": 400,
        }
    if settings.ENABLE_LANGSMITH_TRACING:
        client.update_feedback(
            feedback_id,
            score=data.get("score"),
            comment=data.get("comment"),
        )
    # TODO: add langfuse feedback
    return {"result": "patched feedback successfully", "code": 200}


@router.post("/get_trace")
async def get_trace(request: Request):
    data = await request.json()
    run_id = data.get("run_id")
    if run_id is None:
        return {
            "result": "No LangSmith run ID provided",
            "code": 400,
        }
    if settings.ENABLE_LANGSMITH_TRACING:
        return await aget_trace_url(run_id, client)
    # TODO: add langfuse feedback
    return {"result": "no trace url", "code": 200}

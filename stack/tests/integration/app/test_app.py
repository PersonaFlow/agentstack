from typing import Optional, Sequence
from uuid import uuid4

import asyncpg

from tests.integration.app.helpers import get_client


def _project(d: dict, *, exclude_keys: Optional[Sequence[str]]) -> dict:
    """Return a dict with only the keys specified."""
    _exclude = set(exclude_keys) if exclude_keys else set()
    return {k: v for k, v in d.items() if k not in _exclude}


async def test_list_and_create_assistants(pool: asyncpg.pool.Pool) -> None:
    """Test list and create assistants."""
    headers = {"X-API-KEY": "1234"}
    assistant_id = str(uuid4())

    async with pool.acquire() as conn:
        assert len(await conn.fetch("SELECT * FROM assistants;")) == 0

    async with get_client() as client:
        response = await client.get(
            "/assistants/",
            headers=headers,
        )
        assert response.status_code == 200

        assert response.json() == []

        # Create an assistant
        # response = await client.patch(
        #     f"/assistants/{assistant_id}",
        #     json={"name": "bobby", "config": {}, "public": False},
        #     headers=headers,
        # )
        # assert response.status_code == 200
        # assert _project(response.json(), exclude_keys=["updated_at", "user_id"]) == {
        #     "assistant_id": assistant_id,
        #     "config": {},
        #     "name": "bobby",
        #     "public": False,
        # }
        # async with pool.acquire() as conn:
        #     assert len(await conn.fetch("SELECT * FROM assistant;")) == 1

        # response = await client.get("/assistants/", headers=headers)
        # assert [
        #     _project(d, exclude_keys=["updated_at", "user_id"]) for d in response.json()
        # ] == [
        #     {
        #         "assistant_id": assistant_id,
        #         "config": {},
        #         "name": "bobby",
        #         "public": False,
        #     }
        # ]

        # response = await client.put(
        #     f"/assistants/{assistant_id}",
        #     json={"name": "bobby", "config": {}, "public": False},
        #     headers=headers,
        # )

        # assert _project(response.json(), exclude_keys=["id", "user_id"]) == {
        #     "assistant_id": assistant_id,
        #     "config": {},
        #     "name": "bobby",
        #     "public": False,
        # }

        # # TODO: Check not visible to other users
        # headers = {"Cookie": "opengpts_user_id=2"}
        # response = await client.get("/assistants/", headers=headers)
        # assert response.status_code == 200, response.text
        # assert response.json() == []


# async def test_threads() -> None:
#     """Test put thread."""
#     headers = {"Cookie": "opengpts_user_id=1"}
#     aid = str(uuid4())
#     tid = str(uuid4())

#     async with get_client() as client:
#         response = await client.patch(
#             f"/assistants/{aid}",
#             json={
#                 "name": "assistant",
#                 "config": {"configurable": {"type": "chatbot"}},
#                 "public": False,
#             },
#             headers=headers,
#         )

#         response = await client.patch(
#             f"/threads/{tid}",
#             json={"name": "bobby", "assistant_id": aid},
#             headers=headers,
#         )
#         assert response.status_code == 200, response.text

#         response = await client.get(f"/threads/{tid}/state", headers=headers)
#         assert response.status_code == 200
#         assert response.json() == {"values": None, "next": []}

#         response = await client.get("/threads/", headers=headers)

#         assert response.status_code == 200
#         assert [
#             _project(d, exclude_keys=["updated_at", "user_id"]) for d in response.json()
#         ] == [
#             {
#                 "assistant_id": aid,
#                 "name": "bobby",
#                 "thread_id": tid,
#                 "metadata": {"assistant_type": "chatbot"},
#             }
#         ]

#         response = await client.put(
#             f"/threads/{tid}",
#             headers={"Cookie": "opengpts_user_id=2"},
#         )
#         assert response.status_code == 422

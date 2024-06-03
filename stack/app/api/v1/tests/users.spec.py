# import pytest
# from httpx import AsyncClient
# from main import app

# @pytest.fixture
# async def client():
#     async with AsyncClient(app=app, base_url="http://localhost:9000") as ac:
#         yield ac

# @pytest.mark.asyncio
# async def test_create_user(client):
#     response = await client.post("/users", json={"user_id": "123456", "email": "test@example.com"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["user_id"] == "123456"
#     assert data["email"] == "test@example.com"

# @pytest.fixture
# async def test_user(client):
#     user_data = {"user_id": "654321", "email": "john.doe@example.com"}
#     response = await client.post("/users", json=user_data)
#     user = response.json()
#     return user

# @pytest.mark.asyncio
# async def test_retrieve_user(client, test_user):
#     user_id = test_user["user_id"]
#     response = await client.get(f"/users/{user_id}")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["email"] == "john.doe@example.com"

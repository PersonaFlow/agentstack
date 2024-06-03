import pytest
from httpx import AsyncClient

from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings

app = create_app(Settings())

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://localhost:9000") as ac:
        yield ac


async def test_healthcheck(client):
    response = await client.get('/health_check')
    assert response.status_code == 200

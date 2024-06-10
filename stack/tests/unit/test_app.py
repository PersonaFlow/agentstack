from starlette.testclient import TestClient

from stack.app.app_factory import create_app
from stack.app.core.configuration import Settings

app = create_app(Settings())
client = TestClient(app)


async def test__app__healthcheck():
    response = client.get("/api/v1/health_check")
    assert response.status_code == 200

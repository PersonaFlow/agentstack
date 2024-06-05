async def test__app__healthcheck(client):
    response = await client.get("/api/v1/health_check")
    assert response.status_code == 200

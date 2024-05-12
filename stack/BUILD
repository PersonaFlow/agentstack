python_sources(name="lib")

pex_binary(
    name="local",
    entry_point="app/main.py",
    dependencies=["//:reqs#asyncpg", "//:reqs#python-multipart"],
    execution_mode="venv",
)

docker_image(
    name="docker",
)

shell_sources()

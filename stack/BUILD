python_sources(name="lib")

pex_binary(
    name="local",
    entry_point="app/main.py",
    dependencies=["//:reqs#asyncpg", "//:reqs#python-multipart"],
)

docker_image(
    name="docker",
)

shell_sources()

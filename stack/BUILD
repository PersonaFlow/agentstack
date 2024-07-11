python_sources(name="lib")

pex_binary(
    name="local",
    entry_point="app/main.py",
    dependencies=["//:reqs#asyncpg", "//:reqs#python-multipart", "//:reqs#itsdangerous"],
    execution_mode="venv",
)

docker_image(
    name="docker",
    dependencies=[":local"],
    repository="personaflow/stack"
)

shell_sources()

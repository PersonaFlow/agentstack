poetry_requirements(name="reqs")

python_tests(
    name="tests",
    dependencies=["//:test-reqs"]
)

target(
    name="test-reqs",
    dependencies=[
      "//:reqs#asyncpg",
      "//:reqs#python-multipart",
      "//:reqs#pytest-asyncio"
    ]
)

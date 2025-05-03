init:
    poetry install

lint:
    poetry run ruff check .

format:
    poetry run ruff format .

test:
    poetry run pytest -q

run topic:
    poetry run oneforall demo {{topic}}

ci:
    just lint && just format --check && just test

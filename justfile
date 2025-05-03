init:
	poetry install

lint:
	poetry run ruff check .

lint-fix:
	poetry run ruff check . --fix

format:
	poetry run ruff format .

test:
	poetry run pytest -q

run topic:
	poetry run oneforall "{{topic}}"

up:
	docker compose -f docker/docker-compose.yml up -d

down:
	docker compose -f docker/docker-compose.yml down

ci:
	just lint
	just format --check
	just test

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

plan topic:
	poetry run oneforall plan "{{topic}}"

search topic:
	poetry run oneforall search "{{topic}}"

summarize topic:
	poetry run oneforall summarize "{{topic}}"

run topic:
	just search "{{topic}}"

pipeline topic:
	poetry run oneforall plan "{{topic}}" | tee plan.json
	poetry run oneforall search "{{topic}}" > hits.json

up:
	docker compose -f docker/docker-compose.yml up --build -d

down:
	docker compose -f docker/docker-compose.yml down

ci:
	just lint
	just format --check
	just test

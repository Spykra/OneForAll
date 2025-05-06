FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./
RUN pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

COPY src ./src
RUN poetry install --only-root --no-interaction --no-ansi

ENTRYPOINT ["oneforall"]

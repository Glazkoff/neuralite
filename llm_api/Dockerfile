# Dockerfile

FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /fastApiApp

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-root

COPY . /fastApiApp/llm_api/

ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["poetry", "run", "uvicorn", "llm_api.main:app", "--host", "0.0.0.0", "--port", "9001"]
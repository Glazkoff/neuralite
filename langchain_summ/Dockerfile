FROM intel/intel-optimized-pytorch:latest

RUN apt-get update && pip install poetry

RUN poetry config virtualenvs.create false

WORKDIR /code/langchain_summ

COPY ./pyproject.toml ./README.md ./poetry.lock* ./

# COPY ./packages ./packages

# RUN poetry install  --no-interaction --no-ansi --no-root

# COPY * ./

COPY ./app ./app

RUN poetry install --no-interaction --no-ansi

EXPOSE 8080

WORKDIR /code/

CMD exec uvicorn langchain_summ.app.server:app --host 0.0.0.0 --port 8080

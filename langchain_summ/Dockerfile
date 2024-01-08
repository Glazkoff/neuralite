FROM nvidia/cuda:12.1.0-base-ubuntu20.04 AS runtime

RUN apt -y update \
  && apt-get -y install software-properties-common \
  && add-apt-repository ppa:deadsnakes/ppa \
  && apt-get -y install python3.10 python3.10-dev python3.10-distutils python3-pip curl \ 
  && apt-get clean \
  && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10 \
  && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1  \
  && python3.10 -m pip install poetry

ENV POETRY_NO_INTERACTION=1 \
  POETRY_CACHE_DIR=/tmp/poetry_cache

RUN poetry config virtualenvs.create false

WORKDIR /code/langchain_summ

COPY ./pyproject.toml ./README.md ./poetry.lock* ./

COPY ./models ./models

COPY ./app ./app

RUN poetry install --no-interaction --no-ansi --without dev && rm -rf "$POETRY_CACHE_DIR"

EXPOSE 8080

WORKDIR /code/

CMD exec uvicorn langchain_summ.app.server:app --host 0.0.0.0 --port 8080

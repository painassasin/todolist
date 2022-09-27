FROM python:3.10-slim

WORKDIR /opt/

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    PYTHON_PATH=/opt/todolist \
    POETRY_VERSION=1.1.13

RUN groupadd --system service && useradd --system -g service api

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get autoclean && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && pip install "poetry==$POETRY_VERSION" \
    && poetry config virtualenvs.create false

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN poetry install --no-root --no-dev

COPY . .

USER api

ENTRYPOINT ["bash", "entrypoint.sh"]

FROM python:3.10-slim
MAINTAINER painassasin@icloud.com

WORKDIR /opt/

RUN groupadd --system service && useradd --system -g service api

EXPOSE 8000

RUN pip install "poetry==1.1.13"

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi --no-root

COPY . .

USER api

ENTRYPOINT ["bash", "entrypoint.sh"]

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

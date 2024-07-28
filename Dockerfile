# syntax=docker/dockerfile:1

FROM python:3.10
WORKDIR /

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.8.3

RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

CMD [ "poetry", "run", "gunicorn", "-w", "4", "--bind", "0.0.0.0:20001", "backend:create_app()"]

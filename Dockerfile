# syntax=docker/dockerfile:1

FROM python:3.10
WORKDIR /app

COPY . .
RUN poetry install --no-root

CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "backend:create_app()"]

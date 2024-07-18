# syntax=docker/dockerfile:1

FROM python:3.10
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .
RUN python3 -m flask --app backend init-db

CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "backend:create_app()"]

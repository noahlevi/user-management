FROM python:3.10-slim AS dev

WORKDIR /app

COPY requirements/dev.txt .

RUN pip install --no-cache-dir --upgrade -r dev.txt

COPY user_management user_management
COPY config config

EXPOSE 8080

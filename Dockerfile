FROM node:14-slim as ui

COPY ui /ui
WORKDIR /ui
RUN yarn && yarn build

FROM python:3.9-slim as poetry
RUN pip install poetry
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN poetry export -f requirements.txt > requirements.txt

FROM debian:11-slim
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -yqq python3-pip sqlite3
RUN pip install gunicorn
COPY --from=poetry /requirements.txt /app/requirements.txt
COPY --from=ui /ui/dist /app/ui/dist
RUN pip install -r requirements.txt

COPY schema.sql /app/schema.sql
COPY app.py /app/app.py
CMD gunicorn --bind 0.0.0.0:5000 app:app

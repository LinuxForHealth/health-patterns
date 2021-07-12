# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

WORKDIR /app

COPY pinned.txt pinned.txt

RUN pip3 install -r pinned.txt

COPY . .

ENV FLASK_APP /app/text_analytics/app.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

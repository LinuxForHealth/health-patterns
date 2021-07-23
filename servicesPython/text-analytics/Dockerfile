# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

WORKDIR /app

COPY pinned.txt pinned.txt
COPY setup.py setup.py
COPY setup.properties setup.properties

RUN pip3 install -r pinned.txt

COPY . .

RUN pip3 install .

ENV FLASK_APP /app/text_analytics/app.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

WORKDIR /app

COPY pinned.txt pinned.txt
COPY setup.py setup.py
COPY setup.properties setup.properties

RUN pip3 install -r pinned.txt

COPY . .

RUN pip3 install .

RUN useradd alvearie -m
USER alvearie

ENV FLASK_APP /app/text_analytics/app.py

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster

WORKDIR /app

COPY pinned.txt pinned.txt
COPY setup.py setup.py
COPY setup.properties setup.properties

RUN pip3 install -r pinned.txt

RUN mkdir src && mkdir src/main && mkdir src/main/py
COPY src/main/py src/main/py

RUN pip3 install .

ENV FLASK_APP text_analytics.app

EXPOSE 5000

# must run under non-root user
RUN useradd alvearie
RUN mkdir /home/alvearie
RUN chown -R alvearie: /home/alvearie
RUN chown -R alvearie: /app

USER alvearie
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]

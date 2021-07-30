FROM python:3.8-slim-buster

WORKDIR /app
ENV FLASK_APP=bulkextract.py

RUN pip3 install flask
RUN pip3 install flask-restful
RUN pip3 install requests
RUN pip3 install ibm-cos-sdk

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

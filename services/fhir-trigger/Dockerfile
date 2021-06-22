FROM python:3.8-slim-buster

RUN pip3 install requests
RUN pip3 install kafka-python

ADD fhirtrigger.py /

CMD [ "python3", "./fhirtrigger.py" ]

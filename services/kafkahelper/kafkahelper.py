from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

import os

from flask import Flask, request
from flask import jsonify

from datetime import datetime

app = Flask(__name__)

kafkauser = os.getenv("KAFKAUSER")
kafkapw = os.getenv("KAFKAPW")
kafkabootstrap = os.getenv("KAFKABOOTSTRAP")

@app.route("/healthcheck", methods=['GET'])
def healthcheck():
    now = datetime.now()

    current_time_date = now.strftime("%Y-%m-%d %H:%M:%S")

    message = {
        "status" : "Kafka tool service is running..." + current_time_date + "GMT"
    }
    resp = jsonify(message)
    resp.status_code = 200

    return resp

@app.route("/topics", methods=['GET'])
def gettopics():
    consumer = KafkaConsumer(bootstrap_servers=kafkabootstrap,
                             sasl_mechanism="PLAIN", sasl_plain_username=kafkauser, sasl_plain_password=kafkapw)

    existingtopics = consumer.topics()

    message = {
        "status": "200",
        "topics": str(existingtopics)
    }
    resp = jsonify(message)
    resp.status_code = 200

    return resp

@app.route("/produce", methods=['POST'])
def produce():
    resolveterminology = request.headers.get("ResolveTerminology", "false")
    deidentifydata = request.headers.get("DeidentifyData", "false")
    runascvd = request.headers.get("RunASCVD", "false")
    resourceid = request.headers.get("ResourceId", "")

    headers = [("ResolveTerminology",bytes(resolveterminology, 'utf-8')),
               ("DeidentifyData",bytes(deidentifydata, 'utf-8')),
               ("RunASCVD",bytes(runascvd, 'utf-8'))]

    if len(resourceid) > 0:
        headers.append(("ResourceId", bytes(resourceid, 'utf-8')))

    topic = ""
    if 'topic' in request.args:
        topic = request.args.get("topic")

    if len(topic) == 0:
        #no topic 400 error
        message = {
            "status": "400",
            "message": "Topic not found: must include a topic for produce"
        }
        resp = jsonify(message)
        resp.status_code = 400

        return resp


    post_data = request.data.decode("utf-8")

    producer = KafkaProducer(bootstrap_servers=kafkabootstrap)

    producer.send(topic, value=bytes(post_data, 'utf-8'), headers=headers)
    producer.flush()
    message = {
        "status": "200",
        "topic": topic,
        "headers": str(headers),
        "data": post_data[0:25] + "... " + str(len(post_data)) + " chars"
    }
    resp = jsonify(message)
    resp.status_code = 200

    return resp

@app.route("/consume", methods=['GET'])
def consume():
    topic = ""
    if 'topic' in request.args:
        topic = request.args.get("topic")

    if len(topic) == 0:
        #no topic 400 error
        message = {
            "status": "400",
            "message": "Topic not found: must include a topic for consume"
        }
        resp = jsonify(message)
        resp.status_code = 400

        return resp

    consumer = KafkaConsumer(topic, bootstrap_servers=kafkabootstrap,
                             sasl_mechanism="PLAIN", sasl_plain_username=kafkauser, sasl_plain_password=kafkapw,
                             consumer_timeout_ms=2000)

    existingtopics = consumer.topics()
    if topic not in existingtopics:
        # no topic 400 error
        message = {
            "status": "400",
            "message": "Topic not found: selected topic does not exist"
        }
        resp = jsonify(message)
        resp.status_code = 400

        return resp

    consumer.topics()
    consumer.seek_to_beginning()

    msglist = []
    for msg in consumer:
        msglist.append("\nMessage: " + str(msg))

    nummessages = len(msglist)
    messages = "\n".join(msglist)

    #datastring = "Messages on queue: " + str(nummessages) + "\n\n" + messages

    message = {
        "status": "200",
        "topic": topic,
        "nummessages": nummessages,
        "data": messages
    }
    resp = jsonify(message)
    resp.status_code = 200

    return resp

@app.route("/createtopic", methods=['POST'])
def create():
    topic = ""
    if 'topic' in request.args:
        topic = request.args.get("topic")

    if len(topic) == 0:
        # no topic 400 error
        message = {
            "status": "400",
            "message": "Topic not found: must include a topic"
        }
        resp = jsonify(message)
        resp.status_code = 400

        return resp

    consumer = KafkaConsumer(topic, bootstrap_servers=kafkabootstrap,
                             sasl_mechanism="PLAIN", sasl_plain_username=kafkauser, sasl_plain_password=kafkapw,
                             consumer_timeout_ms=2000)

    existingtopics = consumer.topics()

    if topic in existingtopics:
        # existing topic 400 error
        message = {
            "status": "400",
            "message": "Topic already exists: cannot recreate existing topic"
        }
        resp = jsonify(message)
        resp.status_code = 400

        return resp

    admin_client = KafkaAdminClient(
        bootstrap_servers=kafkabootstrap,
        client_id="bootstrapclient"
    )

    topic_list = []
    topic_list.append(NewTopic(name=topic, num_partitions=1, replication_factor=1))
    admin_client.create_topics(new_topics=topic_list, validate_only=False)

    message = {
        "status": "200",
        "topic": topic,
        "message": "topic created"
    }
    resp = jsonify(message)
    resp.status_code = 200
    return resp

if __name__ == '__main__':
   app.run()

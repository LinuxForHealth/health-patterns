# Test comment

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

# create the kafka topics before use
initial_topics = os.getenv("INITTOPICS", "")  #empty list if missing
numpartitions = os.getenv("INITTOPICNUMPARTITIONS", "1")
if len(numpartitions) == 0:
    numpartitions = 1
else:
    numpartitions = int(numpartitions)

replication = os.getenv("INITTOPICREPLICATION", "1")
if len(replication) == 0:
    replication = 1
else:
    replication = int(replication)

init_topics = initial_topics.replace(",", " ")
topiclist = init_topics.split()

while True:
    try:
        KafkaConsumer(bootstrap_servers=kafkabootstrap,
                                 sasl_mechanism="PLAIN", sasl_plain_username=kafkauser, sasl_plain_password=kafkapw)
        break
    except:
        pass # Ignore error-just retry

# kafka is now up and running

initconsumer = KafkaConsumer(bootstrap_servers=kafkabootstrap,
                         sasl_mechanism="PLAIN", sasl_plain_username=kafkauser, sasl_plain_password=kafkapw)

existing_topics = initconsumer.topics()

init_admin_client = KafkaAdminClient(
    bootstrap_servers=kafkabootstrap,
    client_id="initbootstrapclient"
)

new_topic_list = []
for new_topic in topiclist:
    if new_topic not in existing_topics:
        new_topic_list.append(NewTopic(name=new_topic, num_partitions=numpartitions, replication_factor=replication))
init_admin_client.create_topics(new_topics=new_topic_list, validate_only=False)

existing_topics = initconsumer.topics() #reset the existing_topics since new ones may have been added

for atopic in existing_topics:
    initconsumer.partitions_for_topic(atopic) # populate cache for each topic


@app.route("/healthcheck", methods=['GET'])
def healthcheck():

    now = datetime.now()
    current_time_date = now.strftime("%Y-%m-%d %H:%M:%S")
    return generate_response(200, {"message": "Kafka tool service is running..." + current_time_date + "GMT"})

@app.route("/", methods=['GET'])
def listorconsumetopics():
    topic = ""
    if 'topic' in request.args:
        topic = request.args.get("topic")

    if len(topic) == 0: #topic arg not present so do topiclist
        consumer = KafkaConsumer(bootstrap_servers=kafkabootstrap,
                                 sasl_mechanism="PLAIN", sasl_plain_username=kafkauser, sasl_plain_password=kafkapw)

        existingtopics = consumer.topics()

        return generate_response(200, {"topics": str(existingtopics)})

    #consume the given topic
    consumer = KafkaConsumer(topic, bootstrap_servers=kafkabootstrap,
                             sasl_mechanism="PLAIN", sasl_plain_username=kafkauser, sasl_plain_password=kafkapw,
                             consumer_timeout_ms=2000)

    existingtopics = consumer.topics()
    if topic not in existingtopics:
        return generate_response(400, {"message": "Topic not found: selected topic does not exist"})

    consumer.topics()
    consumer.seek_to_beginning()

    msglist = []
    for msg in consumer:
        msglist.append("\nMessage: " + str(msg))

    nummessages = len(msglist)
    messages = "\n".join(msglist)

    return generate_response(200, {"topic": topic,
                                   "nummessages": nummessages,
                                   "data": messages})

@app.route("/", methods=['POST'])
def produce():
    resolveterminology = request.headers.get("ResolveTerminology", "false")
    deidentifydata = request.headers.get("DeidentifyData", "false")
    runascvd = request.headers.get("RunASCVD", "false")
    add_nlp_insights = request.headers.get("AddNLPInsights", "false")
    resourceid = request.headers.get("ResourceId", "")

    headers = [
                ("ResolveTerminology",bytes(resolveterminology, 'utf-8')),
                ("DeidentifyData",bytes(deidentifydata, 'utf-8')),
                ("RunASCVD",bytes(runascvd, 'utf-8')),
                ("AddNLPInsights",bytes(add_nlp_insights, 'utf-8'))
               ]

    if len(resourceid) > 0:
        headers.append(("ResourceId", bytes(resourceid, 'utf-8')))

    topic = ""
    if 'topic' in request.args:
        topic = request.args.get("topic")

    if len(topic) == 0:
        #no topic 400 error
        return generate_response(400, {"message": "Topic not found: must include a topic for produce (POST)"})

    post_data = request.data.decode("utf-8")

    producer = KafkaProducer(bootstrap_servers=kafkabootstrap, max_request_size=10000000)

    producer.send(topic, value=bytes(post_data, 'utf-8'), headers=headers)
    producer.flush()

    return generate_response(200, {"topic": topic,
                                   "headers": str(headers),
                                   "data": post_data[0:25] + "... " + str(len(post_data)) + " chars"})

@app.route("/", methods=['PUT'])
def create():
    topic = ""
    if 'topic' in request.args:
        topic = request.args.get("topic")

    if len(topic) == 0:
        # no topic 400 error
        return generate_response(400, {"message": "Topic not found: must include a topic to create (PUT)"})

    consumer = KafkaConsumer(topic, bootstrap_servers=kafkabootstrap,
                             sasl_mechanism="PLAIN", sasl_plain_username=kafkauser, sasl_plain_password=kafkapw,
                             consumer_timeout_ms=2000)

    existingtopics = consumer.topics()

    if topic in existingtopics:

        return generate_response(400, {"message": "Topic already exists: cannot recreate existing topic"})

    admin_client = KafkaAdminClient(
        bootstrap_servers=kafkabootstrap,
        client_id="bootstrapclient"
    )

    topic_list = []
    topic_list.append(NewTopic(name=topic, num_partitions=1, replication_factor=1))
    admin_client.create_topics(new_topics=topic_list, validate_only=False)

    return generate_response(200, {"topic": topic,
                                   "message": "topic created"})

def generate_response(statuscode, otherdata={}):

    message = {
        "status": str(statuscode)
    }
    message.update(otherdata)
    resp = jsonify(message)
    resp.status_code = statuscode
    return resp



if __name__ == '__main__':
   app.run()

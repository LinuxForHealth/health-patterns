from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

import json
import threading
import time
import os

import requests
import datetime

import uuid

#global lock for keeping kafka safe
kafkalock = threading.Lock()

def history():
    #Fill in the configuration from env variables related to history triggers
    chunksize = int(os.getenv("CHUNKSIZE"))
    rlist = os.getenv("RESOURCESLIST").split()
    sleepseconds = int(os.getenv("SLEEPSECONDS"))
    kafkabootstrap = os.getenv("KAFKABOOTSTRAP")
    producertopic = os.getenv("PRODUCERTOPIC")
    fhirEndpoint=os.getenv("FHIRENDPOINT")
    fhirusername=os.getenv("FHIRUSERNAME")
    fhirpassword=os.getenv("FHIRPW")

    producer = KafkaProducer(bootstrap_servers=kafkabootstrap)

    afterhistoryid = 0
    while True: #do this forever waking up every so often to check for recent history news
        historyurl = fhirEndpoint + "/_history?_count=" + str(chunksize) + "&_afterHistoryId=" + str(afterhistoryid)
        resp = requests.get(historyurl, auth=(fhirusername, fhirpassword))

        if (resp.status_code == 200):
            historydict = resp.json()
            if "entry" in historydict:
                #new history items to consider
                for alink in historydict["link"]:
                    if alink['relation'] == 'next':
                        nexturl = alink['url']
                        parts = nexturl.split("afterHistoryId=")
                        afterhistoryid = parts[1] #set up the next get request
                        print("RESET afterid to", afterhistoryid)
                        break

                #go through the history resources looking for patient, condition, procedure, observation
                patientids = set()  #empty set of patient ids
                for resource in historydict["entry"]:
                    if resource["request"]["method"] in ["POST", "PUT"]:
                        parts = resource["fullUrl"].split("/")
                        resourcetype = parts[0]
                        resourceid = parts[1]
                        if resourcetype == "Patient":
                            patientids.add(resourceid)
                        else:
                            # Use search to get patient id
                            if resourcetype in ["Condition", "Observation", "Procedure"]:
                                #get the resource and find the subject
                                resourceurl = fhirEndpoint + "/" +resource["fullUrl"]
                                resp = requests.get(resourceurl, auth=(fhirusername, fhirpassword))
                                if resp.status_code == 200:
                                    resourceresp = resp.json()
                                    patientid = resourceresp["subject"]["reference"].split("/")[-1]
                                    if ":" in patientid:
                                        patientid = patientid.split(":")[-1]
                                    patientids.add(patientid)

                            # Use backward chaining to get patient id
                            # if resourcetype in ["Condition", "Observation", "Procedure"]:
                            #     # use reverse chaining to get patient from resource
                            #     reverseurl = fhirEndpoint + "/Patient?_has:" + resourcetype + ":patient:_id=" + resourceid
                            #     reverseresp = requests.get(reverseurl, auth=(fhirusername, fhirpassword))
                            #     reversedict = reverseresp.json()
                            #     patientid = reversedict["entry"][0]["resource"]["id"]
                            #     patientids.add(patientid)

                if len(patientids) == 0:
                    print("No new history data...")
                else:
                    print("Patient ids for that chunk", patientids)

                #now process those patients

                for pid in patientids:
                    buildandpushtokafka(pid, rlist, producer, producertopic, fhirEndpoint, fhirusername, fhirpassword)

            else:
                print("No new history items--just sleep and recheck")
        else:
            print("Error getting request--sleep and try again")

        time.sleep(sleepseconds)
        print("Rechecking for new history...")

# This helper method will build a fhir bundle for a given patient and push it to the
# configured kafka endpoint, regardless of how the patient id was found (history or notification)
def buildandpushtokafka(pid, rlist, producer, producertopic, fhirEndpoint, fhirusername, fhirpassword):
    newbundle = None
    resource_list = []

    # Use the $everything operator to get the resources for this patient
    everything_resp = requests.get(
        fhirEndpoint + "/Patient/" + pid + "/$everything?_format=json",
        auth=(fhirusername, fhirpassword), verify=False)

    if everything_resp.status_code == 200:
        everything = everything_resp.json()

        newbundle = everything_resp.json()  # start with the original everything bundle
        del newbundle["total"]
        newbundle["type"] = "transaction"
        newbundle["id"] = str(uuid.uuid4())  # create a random bundle id

        entrylist = None
        if "entry" not in newbundle:
            entrylist = []
        else:
            entrylist = newbundle["entry"]
            for entry in entrylist: #only keep those that have been configured (* means keep everything)
                if (entry["resource"]["resourceType"] in rlist) or ("*" in rlist):
                    entry["fullUrl"] = "urn:uuid::" + entry["resource"]["id"]
                    #transaction bundle needs proper request
                    entry["request"] = { "method": "POST", "url": entry["resource"]["resourceType"]}
                    # need to remove certain parts of entry
                    if "search" in entry:
                        del entry["search"]
                    if "meta" in entry["resource"]:
                        del entry["resource"]["meta"]

                    resource_list.append(entry)  # keep this entry

            newbundle["entry"] = resource_list  # replace entry list
            print("Newbundle created...", newbundle["id"])
            #send resulting bundle to kafka
            kafkalock.acquire(blocking=True)
            print("Sending bundle to kafka...")
            producer.send(producertopic, bytes(json.dumps(newbundle), 'utf-8'))
            kafkalock.release()
    else:
        print("Bad $everything request-no bundle created for", pid)

# notification thread for a patient being processed
class Notificationthread(threading.Thread):
   def __init__(self, pid, timestamp, maxiterations, producer, producertopic,
                fhirendpoint, username, password, resourcelist, createtime, alarmminutes):
      threading.Thread.__init__(self)
      self.name = pid
      self.timestamp = timestamp
      self.maxiterations = maxiterations
      self.iterations = maxiterations #start at max
      self.status = "alive"
      self.producer = producer #connection to the kafka broker to write results
      self.topic = producertopic
      self.fhirendpoint = fhirendpoint
      self.username = username
      self.password = password
      self.resourcelist = resourcelist
      self.createtime = createtime
      self.alarmminutes = alarmminutes

   def getstatus(self):
      return self.status

   def setstatus(self, state):
      self.status = state

   def getcounter(self):
      return self.iterations

   def reset(self):
      self.iterations = self.maxiterations

   def run(self):
      print("Starting thread: " + self.name)
      futurealarm = datetime.datetime.now() + datetime.timedelta(minutes=self.alarmminutes)
      stop = False
      while not stop:
          time.sleep(1)
          self.iterations = self.iterations - 1
          if self.iterations <= 0:
              stop = True
          if datetime.datetime.now() >= futurealarm:
              stop = True

      self.status = 'complete'

      #timer went off for this group so grab resources and create a bundle
      #   with configured resources
      #produce the result bundle on the kafka topic

      buildandpushtokafka(self.name, self.resourcelist, self.producer, self.topic, self.fhirendpoint,
                          self.username, self.password)

      print("Exiting " + self.name)


def notification():
    #Fill in the configuration from env variables
    maxiters = int(os.getenv("MAXITERATIONS"))
    rlist = os.getenv("RESOURCESLIST").split()
    alarmminutes = int(os.getenv("ALARMMINUTES"))
    consumertopic = os.getenv("CONSUMERTOPIC")
    kafkauser = os.getenv("KAFKAUSER")
    kafkapw = os.getenv("KAFKAPW")
    kafkabootstrap = os.getenv("KAFKABOOTSTRAP")
    producertopic = os.getenv("PRODUCERTOPIC")
    fhirEndpoint=os.getenv("FHIRENDPOINT")
    fhirusername=os.getenv("FHIRUSERNAME")
    fhirpassword=os.getenv("FHIRPW")

    #set up the consumer for fhir notifications
    consumer = KafkaConsumer(consumertopic, bootstrap_servers=kafkabootstrap,
                             sasl_mechanism="PLAIN", sasl_plain_username=kafkauser, sasl_plain_password=kafkapw)

    existingtopics = consumer.topics()
    print("Initial topics: ", existingtopics)

    preexist = False  #do we need to create the consumer topic?
    if consumertopic not in existingtopics:
        print("Topic not there...need to create...", consumertopic)

        admin_client = KafkaAdminClient(
            bootstrap_servers=kafkabootstrap,
            client_id="bootstrapclient"
        )

        topic_list = []
        topic_list.append(NewTopic(name=consumertopic, num_partitions=1, replication_factor=1))
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print("Topic created")
    else:
        print("Topic exists...moving ahead to listen on....", consumertopic)
        preexist = True

    #set up the producer to keep ascvd results
    producer = KafkaProducer(bootstrap_servers=kafkabootstrap)

    print("Current topics:", consumer.topics())
    if preexist:
        consumer.seek_to_beginning() #start at the beginning of the notification topic

    notification_thread_dict = {}

    print("Start listening...")
    for msg in consumer:
        parsed = json.loads(msg.value.decode("utf-8"))
        timestamp = msg.timestamp

        resourcetype = parsed["resource"]["resourceType"]
        print("New resource notification", resourcetype)

        patientid = None
        if resourcetype == 'Patient':
            patientid = parsed["location"].split("/")[1]
        else:
            if resourcetype in ['Observation','Condition','Procedure']:
                patientid = parsed["resource"]["subject"]["reference"].split("/")[1]

        if patientid == None: #didn't find a patient id so skip to next message
            continue

        if patientid not in notification_thread_dict:
            print("New pid-create thread",patientid)
            th = Notificationthread(patientid, timestamp, maxiters, producer, producertopic,
                                    fhirEndpoint, fhirusername, fhirpassword, rlist[:], datetime.datetime.now(), alarmminutes)
            notification_thread_dict[patientid] = th
            th.start()
        else:
            if patientid in notification_thread_dict:
                if notification_thread_dict[patientid].getstatus() == 'complete':
                    th = Notificationthread(patientid, timestamp, maxiters, producer, producertopic,
                                            fhirEndpoint, fhirusername, fhirpassword, rlist[:], datetime.datetime.now(), alarmminutes)
                    notification_thread_dict[patientid] = th
                    th.start()
                else:
                    #it is alive so reset the counter
                    notification_thread_dict[patientid].reset()

def main():
    triggertype = os.getenv("TRIGGERTYPE")
    print("Trigger service is configured to use ", triggertype)

    if triggertype == "notification":
        notification()
    else:
        history()

main()

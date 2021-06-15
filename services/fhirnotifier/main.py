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

      newbundle = None
      resource_list = []  #the resources we will keep for new bundle

      #Use the $everything operator to get the resources for this patient
      everything_resp = requests.get(self.fhirendpoint + "/Patient/" + self.name + "/$everything?_format=json",
                                     auth=(self.username, self.password), verify=False)

      if everything_resp.status_code == 200:
          everything = everything_resp.json()

          newbundle = everything_resp.json() #start with the original everything bundle
          del newbundle["total"] #make modifications as needed
          newbundle["type"] = "transaction"
          newbundle["id"] = str(uuid.uuid4()) #create a random bundle id

          entrylist = None
          if "entry" not in newbundle:
              entrylist = []
          else:
              entrylist = newbundle["entry"]
              # go thru all the entries and only keep the ones we want
              for entry in entrylist:
                  if (entry["resource"]["resourceType"] in self.resourcelist) or ("*" in self.resourcelist):
                      entry["fullUrl"] = "urn:uuid::" + entry["resource"]["id"]
                      #need to remove certain parts of entry
                      if "search" in entry:
                          del entry["search"]
                      if "meta" in entry["resource"]:
                          del entry["resource"]["meta"]

                      resource_list.append(entry)  #keep this entry

              newbundle["entry"] = resource_list #replace entry list with the editted resource list

              # send resulting bundle to kafka
              kafkalock.acquire(blocking=True)
              self.producer.send(self.topic, bytes(json.dumps(newbundle), 'utf-8'))
              kafkalock.release()
      else:
          print("Bad $everything request-no bundle created")

      print("Exiting " + self.name)

#global lock for keeping kafka safe
kafkalock = threading.Lock()

def main():
    #print(os.environ)

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

        print("PID", patientid) #from the notification

        if patientid not in notification_thread_dict:
            print("New pid-create thread",patientid)
            th = Notificationthread(patientid, timestamp, maxiters, producer, producertopic,
                                    fhirEndpoint, fhirusername, fhirpassword, rlist[:], datetime.datetime.now(), alarmminutes)
            notification_thread_dict[patientid] = th
            th.start()
        else:
            if patientid in notification_thread_dict:
                print("Existing pid-check liveness", patientid)
                #is it complete, if so start over
                if notification_thread_dict[patientid].getstatus() == 'complete':
                    print("Existing pid is complete, restarting new thread", patientid)
                    th = Notificationthread(patientid, timestamp, maxiters, producer, producertopic,
                                            fhirEndpoint, fhirusername, fhirpassword, rlist[:], datetime.datetime.now(), alarmminutes)
                    notification_thread_dict[patientid] = th
                    th.start()
                else:
                    #it is alive so reset the counter
                    print("Existing pid is still running so reset", patientid)
                    notification_thread_dict[patientid].reset()
                    print("Resetting to", patientid, notification_thread_dict[patientid].getcounter())

main()

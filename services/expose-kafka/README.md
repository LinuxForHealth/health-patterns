# expose-kafka

A deployable service to assist with kafka interaction.

## operations

- listing topics-this will provide a list of all topics
current registered with the kafka broker

    (GET)  https://\<expose-kafkabaseurl:port>

- consuming from a topic-this will show all messages currently
on the topic, starting from the beginning

    (GET)  https://\<expose-kafkabaseurl:port>?topic=\<topicname>

- producing to a topic-place a message on a particular topic

    (POST) https://\<expose-kafkabaseurl:port>?topic=\<topicname>

- producing to a topic-place a message on a particular topic and waiting for a response

    (POST) https://\<expose-kafkabaseurl:port>?topic=\<topicname>&response_topic=<response_topic_name>

- producing to a topic-place a message on a particular topic and waiting for a response or failure

    (POST) https://\<expose-kafkabaseurl:port>?topic=\<topicname>&response_topic=<response_topic_name>&failure_topic=<failure_topic_name>

- creating a new (empty) topic-create a new topic but it will be empty

    (PUT) https://\<expose-kafkabaseurl:port>?topic=\<topicname>

- general health of service-a simple sanity check on the service

    (GET)  https://\<expose-kafkabaseurl:port>/healthcheck

# expose-kafka

A deployable service to assist with kafka interaction.

## operations

- listing topics-this will provide a list of all topics
current registered with the kafka broker

    (GET)  https://\<kafkahelperbaseurl:port>

- consuming from a topic-this will show all messages currently
on the topic, starting from the beginning

    (GET)  https://\<kafkahelperbaseurl:port>?topic=\<topicname>

- producing to a topic-place a message on a particular topic

    (POST) https://\<kafkahelperbaseurl:port>?topic=\<topicname>

- creating a new (empty) topic-create a new topic but it will be empty

    (PUT) https://\<kafkahelperbaseurl:port>?topic=\<topicname>

- general health of service-a simple sanity check on the service

    (GET)  https://\<kafkahelperbaseurl:port>/healthcheck


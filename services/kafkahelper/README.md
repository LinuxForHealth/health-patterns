# kafkahelper

A deployable service to assist with kafka interaction

- listing topics

(GET)  https://kafkahelperbaseurl

- consuming from a topic

(GET)  https://kafkahelperbaseurl?topic=topicname

- producing to a topic

(POST) https://kafkahelperbaseurl?topic=topicname

- creating a new (empty) topic

(PUT) https://kafkahelperbaseurl?topic=topicname

- general health of service

(GET)  https://kafkahelperbaseurl/healthcheck

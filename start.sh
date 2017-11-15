#!/bin/bash
for number in {1..10}
do
raw = "raw-video-stream-" + $number
person = "person-video-stream-" + $number
face = "face-video-stream-" + $number
~/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic $face
~/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic $person
~/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic $raw
# docker run --network samaritan_kafkanet --name tlindener/samaritan-face-detection
# docker run --network samaritan_kafkanet --name tlindener/samaritan-person-detection
# docker run --network samaritan_kafkanet --name tlindener/samaritan-image-extraction
echo "$number"
done
exit 0

#!/bin/bash
for number in {1..2}
do
raw="raw-video-stream-"$number
person="person-video-stream-"$number
face="face-video-stream-"$number
base="video-stream-"$number
~/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic $face
~/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic $person
~/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic $raw
docker run -itd --network samaritan_kafkanet --name $face tlindener/samaritan-face-detection python -u consumer.py --topic $base
docker run -itd --network samaritan_kafkanet --name  $person tlindener/samaritan-person-detection  python -u consumer.py --topic $base
docker run -itd --network samaritan_kafkanet --name  $raw tlindener/samaritan-frame-extractor  python -u producer.py --topic $raw

echo "$number"
done
exit 0

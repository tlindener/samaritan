#!/bin/bash
for number in {1..10}
do
raw = "raw-video-stream-" + $number
person = "person-video-stream-" + $number
face = "face-video-stream-" + $number
# docker run --network samaritan_kafkanet --name tlindener/samaritan-face-detection
# docker run --network samaritan_kafkanet --name tlindener/samaritan-person-detection
# docker run --network samaritan_kafkanet --name tlindener/samaritan-image-extraction
echo "$number"
done
exit 0

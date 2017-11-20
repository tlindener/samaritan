# coding=utf-8
"""Performs face detection in realtime.

Based on code from https://github.com/shanren7/real_time_face_recognition
"""
# MIT License
#
# Copyright (c) 2017 François Gervais
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from kafka import SimpleProducer, KafkaClient, KafkaConsumer
import argparse
import sys
import time

import cv2
import face
import base64
import json
import io
import cv2
import numpy as np
from PIL import Image
from perfmetrics import metric
from perfmetrics import MetricMod
from perfmetrics import set_statsd_client
from statsd import StatsClient

# Take in base64 string and return PIL image
parser = argparse.ArgumentParser()
parser.add_argument(
    "-b", "--broker", help="Kafka Broker address with port", default="kafkaserver:9092")
parser.add_argument(
    "-t", "--topic", help="Outgoing topic name", default="video-stream-01")
parser.add_argument('--debug', action='store_true',
                    help='Enable some debug outputs.')
args = parser.parse_args()
input_topic = "person-" + args.topic
output_topic = "face-" + args.topic

face_recognition = face.Recognition()
kafka = KafkaClient(args.broker)
producer = SimpleProducer(kafka)
consumer = KafkaConsumer(input_topic, group_id='view', bootstrap_servers=[args.broker])

statsd = StatsClient(host='statsd-1',
                     port=8125,
                     prefix=output_topic)
set_statsd_client(statsd)



def stringToImage(base64_string):
    imgdata = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgdata))

# convert PIL Image to an RGB image( technically a numpy array ) that's compatible with opencv


def toRGB(image):
    return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)


def add_overlays(frame, faces):
    if faces is not None:
        for face in faces:
            face_bb = face.bounding_box.astype(int)
            cv2.rectangle(frame,
                          (face_bb[0], face_bb[1]), (face_bb[2], face_bb[3]),
                          (0, 255, 0), 2)
            if face.name is not None:
                cv2.putText(frame, face.name, (face_bb[0], face_bb[3]),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                            thickness=2, lineType=2)


def main():
    start_time = time.time()

    if args.debug:
        print("Debug enabled")
        face.debug = True

    print("Start consuming data")
    for message in consumer:
        if message is not None:
            print(message.offset)
            data = json.loads(message.value.decode("utf-8"))
            find_faces(message.offset,data)


@metric
@MetricMod(output_topic + ".%s")
def find_faces(message_offset, data):
    image = toRGB(stringToImage(data['image']))
    for index, prediction in enumerate(data['predictions']):
        if prediction['label'] == 'person':
            cropped = image[prediction['top']:prediction['bottom'],
                            prediction['left']:prediction['right']]
            print("classify image")
            faces = face_recognition.identify(cropped)
            if len(faces) > 0:
                data['predictions'][index]['faces'] = []
                for f_face in faces:
                    i_face = {}
                    i_face['bounding_box'] = f_face.bounding_box.tolist()
                    i_face['embedding'] = f_face.embedding.tolist()
                    data['predictions'][index]['faces'].append(i_face)
                    print("Adding face num: " + str(index))
    producer.send_messages(
        output_topic, json.dumps(data).encode('utf-8'))


if __name__ == '__main__':
    main()

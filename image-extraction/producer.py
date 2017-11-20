import time
import cv2
from kafka import KafkaProducer, KafkaClient
import argparse
from perfmetrics import metric
from perfmetrics import MetricMod
from perfmetrics import set_statsd_client
set_statsd_client('statsd://statsd-1:8125')

parser = argparse.ArgumentParser()
parser.add_argument("-i","--input",help="Video Input", default="input.mkv")
parser.add_argument("-b","--broker",help="Kafka Broker address with port",default="kafkaserver:9092")
parser.add_argument("-t","--topic",help="Outgoing topic name", default="raw-video-stream-01")
args = parser.parse_args()

#  connect to Kafka
producer = KafkaProducer(bootstrap_servers=[args.broker])
# Assign a topic
topic = args.topic

def video_emitter(video):
    # Open the video
    video = cv2.VideoCapture(video)
    print(' emitting.....')

    # read the file
    while (video.isOpened):
        # read the image in each frame
        success, image = video.read()
        # check if the file has read to the end
        if not success:
            break
        # convert the image png
        ret, jpeg = cv2.imencode('.jpg', image)
        # Convert the image to bytes and send to kafka
        send_image(jpeg)
        
    # clear the capture
    video.release()
    print('done emitting')

@metric
@MetricMod(topic+".%s")
def send_image(jpeg):
    future = producer.send(topic, jpeg.tobytes())
    result = future.get(timeout=10)
    print(result)

if __name__ == '__main__':
    print("Run Video Emitter")
    video_emitter(args.input)

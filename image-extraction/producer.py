import time
import cv2
from kafka import SimpleProducer, KafkaClient
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i","--input",help="Video Input", default="input.mkv")
parser.add_argument("-b","--broker",help="Kafka Broker address with port",default="kafkaserver:9092")
parser.add_argument("-t","--topic",help="Outgoing topic name", default="raw-video-stream-01")
args = parser.parse_args()

#  connect to Kafka
kafka = KafkaClient(args.broker)
producer = SimpleProducer(kafka)
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
        producer.send_messages(topic, jpeg.tobytes())
        # To reduce CPU usage create sleep time of 0.2sec
        time.sleep(0.2)
    # clear the capture
    video.release()
    print('done emitting')

if __name__ == '__main__':
    print("Run Video Emitter")
    video_emitter(args.input)

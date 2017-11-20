import colorsys
import imghdr
import os
import random
import io
import numpy as np
from kafka import SimpleProducer, KafkaClient, KafkaConsumer
import argparse
from keras import backend as K
from keras.models import load_model
from PIL import Image, ImageDraw, ImageFont
from yad2k.models.keras_yolo import yolo_eval, yolo_head
import base64
import json
from perfmetrics import set_statsd_client
from perfmetrics import metric
from perfmetrics import MetricMod
from statsd import StatsClient

_scoreTreshold = 0.3
_iouTreshold = 0.5

parser = argparse.ArgumentParser()
parser.add_argument(
    "-b", "--broker", help="Kafka Broker address with port", default="kafkaserver:9092")
parser.add_argument(
    "-t", "--topic", help="Outgoing topic name", default="video-stream-01")
args = parser.parse_args()
input_topic = "raw-" + args.topic
output_topic = "person-" + args.topic

statsd = StatsClient(host='statsd-1',
                     port=8125,
                     prefix=output_topic)
set_statsd_client(statsd)

#  connect to Kafka
kafka = KafkaClient(args.broker)
producer = SimpleProducer(kafka)
consumer = KafkaConsumer(input_topic, group_id='view',
                         bootstrap_servers=[args.broker])


@metric
@MetricMod(output_topic+".%s")
def classify(image, image_file):
    # Generate output tensor targets for filtered bounding boxes.
    # TODO: Wrap these backend operations with Keras layers.
    yolo_outputs = yolo_head(yolo_model.output, anchors, len(class_names))
    input_image_shape = K.placeholder(shape=(2, ))
    boxes, scores, classes = yolo_eval(
        yolo_outputs,
        input_image_shape,
        score_threshold=_scoreTreshold,
        iou_threshold=_iouTreshold)

    if is_fixed_size:  # TODO: When resizing we can use minibatch input.
        resized_image = image.resize(
            tuple(reversed(model_image_size)), Image.BICUBIC)
        image_data = np.array(resized_image, dtype='float32')
    else:
        # Due to skip connection + max pooling in YOLO_v2, inputs must have
        # width and height as multiples of 32.
        new_image_size = (image.width - (image.width % 32),
                          image.height - (image.height % 32))
        resized_image = image.resize(new_image_size, Image.BICUBIC)
        image_data = np.array(resized_image, dtype='float32')
        print(image_data.shape)

    image_data /= 255.
    image_data = np.expand_dims(image_data, 0)  # Add batch dimension.

    out_boxes, out_scores, out_classes = sess.run(
        [boxes, scores, classes],
        feed_dict={
            yolo_model.input: image_data,
            input_image_shape: [image.size[1], image.size[0]],
            K.learning_phase(): 0
        })


    data = {}
    data['image'] = getBase64Image(image)
    predictions = []
    thickness = (image.size[0] + image.size[1]) // 300
    for i, c in reversed(list(enumerate(out_classes))):
        predicted_class = class_names[c]
        box = out_boxes[i]
        score = out_scores[i]
        top, left, bottom, right = box
        top = max(0, np.floor(top + 0.5).astype('int32'))
        left = max(0, np.floor(left + 0.5).astype('int32'))
        bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
        right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
        prediction = {}
        prediction['label'] = predicted_class
        prediction['score'] = int(score * 100)
        prediction['top'] = int(top)
        prediction['left'] = int(left)
        prediction['bottom'] = int(bottom)
        prediction['right'] = int(right)
        if predicted_class == "person":
            print(predicted_class)
            draw = ImageDraw.Draw(image)
            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=colors[c])
            del draw
        predictions.append(prediction)

    data['predictions'] = predictions
    data['image_bb'] = getBase64Image(image)
    # print(json.dumps(data))
    print("send message")
    producer.send_messages(output_topic, json.dumps(data).encode('utf-8'))

def getBase64Image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str.decode("utf-8")

def get_classes(classes_path):
    '''loads the classes'''
    with open(classes_path) as f:
        class_names = f.readlines()
    class_names = [c.strip() for c in class_names]
    return class_names


def get_anchors(anchors_path):
    '''loads the anchors from a file'''
    if os.path.isfile(anchors_path):
        with open(anchors_path) as f:
            anchors = f.readline()
            anchors = [float(x) for x in anchors.split(',')]
            return np.array(anchors).reshape(-1, 2)
    else:
        Warning("Could not open anchors file, using default.")
        return np.array(
            ((0.57273, 0.677385), (1.87446, 2.06253), (3.33843, 5.47434),
             (7.88282, 3.52778), (9.77052, 9.16828)))


if __name__ == '__main__':
    print("start person detector")
    model_path = os.path.expanduser('model_data/yolo.h5')
    assert model_path.endswith('.h5'), 'Keras model must be a .h5 file.'
    anchors_path = os.path.expanduser('model_data/yolo_anchors.txt')
    classes_path = os.path.expanduser('model_data/coco_classes.txt')
    test_path = os.path.expanduser('images')
    output_path = os.path.expanduser('images/out')
    if not os.path.exists(output_path):
        print('Creating output path {}'.format(output_path))
        os.mkdir(output_path)
    sess = K.get_session()  # TODO: Remove dependence on Tensorflow session.

    class_names = get_classes(classes_path)
    anchors = get_anchors(anchors_path)

    yolo_model = load_model(model_path)

    # Verify model, anchors, and classes are compatible
    num_classes = len(class_names)
    num_anchors = len(anchors)
    # TODO: Assumes dim ordering is channel last
    model_output_channels = yolo_model.layers[-1].output_shape[-1]
    assert model_output_channels == num_anchors * (num_classes + 5), \
        'Mismatch between model and given anchor and class sizes. ' \
        'Specify matching anchors and classes with --anchors_path and ' \
        '--classes_path flags.'
    print('{} model, anchors, and classes loaded.'.format(model_path))
# Generate colors for drawing bounding boxes.
    hsv_tuples = [(x / len(class_names), 1., 1.)
                  for x in range(len(class_names))]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(
        map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
            colors))
    random.seed(10101)  # Fixed seed for consistent colors across runs.
    # Check if model is fully convolutional, assuming channel last order.
    model_image_size = yolo_model.layers[0].input_shape[1:3]
    is_fixed_size = model_image_size != (None, None)
    print("Start consuming data")
    for message in consumer:
        if message is not None:
            print(message.offset)
            image = Image.open(io.BytesIO(message.value))
            print("classify image")
            classify(image, str(message.offset))

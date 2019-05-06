import os
import cv2
import pickle
from pykafka import KafkaClient
from pykafka.common import OffsetType
import itertools
import time
import random
import sys

IMAGE_DIR_PATH = 'video_to_images'
IMAGE_FREQUENCY = 5
PRODUCER_TYPE = 'loop'


def gen_client(hosts="127.0.0.1:9092", topic_name='people-detection'):
    client = KafkaClient(hosts=hosts)
    topic = client.topics[topic_name]
    return client, topic


def produce(topic, serialized_obj):
    with topic.get_sync_producer(max_request_size=104857600) as producer:
        producer.produce(serialized_obj)


def image_producer_loop(client, topic):
    images = os.listdir(IMAGE_DIR_PATH)
    image_sort = [int(image[6:image.find('.')]) for image in images]
    image_sort.sort()
    images_sorted = []
    for image_idx in image_sort:
        images_sorted.append('frame_{}.jpg'.format(image_idx))

    for image in itertools.cycle(images_sorted):
        img = open('{}/{}'.format(IMAGE_DIR_PATH, image), 'rb').read()
        frame_num = int(image[6:image.find('.')])
        msg = {
            'frame_num': frame_num,
            'img': img
        }
        msg_pickle = pickle.dumps(msg)
        produce(topic, msg_pickle)
        print("Message published")
        # print("Image Size:{}".format(img.shape))
        time.sleep(IMAGE_FREQUENCY)


def image_producer_random(client, topic):
    images = os.listdir(IMAGE_DIR_PATH)
    while True:
        frame = random.choice(images)
        img = open('{}/{}'.format(IMAGE_DIR_PATH, frame), 'rb').read()
        frame_num = int(frame[6:frame.find('.')])
        msg = {
            'frame_num': frame_num,
            'img': img
        }
        msg_pickle = pickle.dumps(msg)
        produce(topic, msg_pickle)
        print("Message published")
        # print("{} - Image Size:{}".format(frame, img.shape))
        time.sleep(IMAGE_FREQUENCY)


if __name__ == "__main__":
    arg_len = len(sys.argv)
    if arg_len > 1:
        IMAGE_DIR_PATH = sys.argv[1]
    if arg_len > 2:
        IMAGE_FREQUENCY = int(sys.argv[2])
    if arg_len > 3:
        PRODUCER_TYPE = sys.argv[3]

    client, topic = gen_client(
        hosts="127.0.0.1:9092", topic_name='people-detection')
    # print(client, topic)
    if PRODUCER_TYPE == 'loop':
        image_producer_loop(client, topic)
    else:
        image_producer_random(client, topic)

# To dos:
# Dockerize the application

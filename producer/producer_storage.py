import os
import cv2
import pickle
from pykafka import KafkaClient
from pykafka.common import OffsetType
import itertools
import time
import random


IMAGE_DIR_PATH = 'video_to_images'
IMAGE_FREQUENCY = 5


def gen_client(hosts="127.0.0.1:9092", topic_name='test'):
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
        img = cv2.imread('{}/{}'.format(IMAGE_DIR_PATH, image))
        frame_num = int(image[6:image.find('.')])
        msg = {
            'frame_num': frame_num,
            'img_arr': img
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
        img = cv2.imread('{}/{}'.format(IMAGE_DIR_PATH, frame))
        frame_num = int(frame[6:frame.find('.')])
        msg = {
            'frame_num': frame_num,
            'img_arr': img
        }
        msg_pickle = pickle.dumps(msg)
        produce(topic, msg_pickle)
        print("Message published")
        # print("{} - Image Size:{}".format(frame, img.shape))
        time.sleep(IMAGE_FREQUENCY)


if __name__ == "__main__":
    client, topic = gen_client(hosts="127.0.0.1:9092", topic_name='test')
    print(client, topic)
    image_producer_loop(client, topic)

# To dos:
# Dockerize the application
# Add sys argv to enable changing the image request frequency

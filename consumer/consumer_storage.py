from PIL import Image
from io import BytesIO
import pickle
import json
import numpy as np
from pykafka import KafkaClient
from pykafka.common import OffsetType


def gen_client(hosts="127.0.0.1:9092", topic_name='people-detection'):
    client = KafkaClient(hosts=hosts)
    topic = client.topics[topic_name]
    return client, topic


def decode(msg):
    msg = pickle.loads(msg)
    return msg


def model(msg):
    """Call the model from here maybe"""
    print('Frame Number:', msg['frame_num'],
          'Image Dimensions:', msg['img_arr'].shape)


if __name__ == "__main__":
    client, topic = gen_client(
        hosts="127.0.0.1:9092", topic_name='people-detection')
    consumer = topic.get_simple_consumer(fetch_message_max_bytes=104857600)
    for msg in consumer:
        if msg is not None:
            msg = decode(msg.value)
            model(msg)


# To dos:
# Dockerize the application
# Improve the consumer - currently it is a simple consumer

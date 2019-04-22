from tornado.ioloop import IOLoop, PeriodicCallback
import pytz
from PIL import Image
import requests
from io import BytesIO
import datetime
import pickle
import json
import numpy as np
from pykafka import KafkaClient
from pykafka.common import OffsetType
from functools import partial

FREQUENCY_SECONDS = 60


def get_image():
    # timenow_et = datetime.datetime.now(pytz.timezone('America/New_York')).strftime('%Y-%m-%d-%H-%M-%S')
    retries = 10
    success = False
    while retries > 0 and success is False:
        response = requests.get('http://cdn.shakeshack.com/camera.jpg')
        if len(response.content) > 0:
            success = True
        retries -= 1
    print('Retries:', 9 - retries)
    return response


def save_image():
    response = get_image()
    if response.status_code == 200:
        req_time = response.headers['date'].replace(
            ' ', '-').replace(':', '-').replace(',', '')
        img = Image.open(BytesIO(response.content))
        img.save(open('shakeshack_image_{}.jpg'.format(req_time), 'wb'))


def gen_client(hosts="127.0.0.1:9092", topic_name='test'):
    client = KafkaClient(hosts=hosts)
    topic = client.topics[topic_name]
    return client, topic


def produce(topic, serialized_obj):
    with topic.get_sync_producer() as producer:
        producer.produce(serialized_obj)


def pub_message(client, topic):
    response = get_image()
    if response.status_code == 200 and len(response.content) > 0:
        req_time = response.headers['date'].replace(
            ' ', '-').replace(':', '-').replace(',', '')
        msg = {
            'req_time': req_time,
            'img_bytes': response.content
        }
        print(len(msg['img_bytes']))
        msg_pickle = pickle.dumps(msg)
        produce(topic, msg_pickle)
        print("Message published")


if __name__ == "__main__":
    client, topic = gen_client(hosts="127.0.0.1:9092", topic_name='test')
    print(client, topic)
    pub_message_args = partial(pub_message, client, topic)
    PeriodicCallback(pub_message_args, FREQUENCY_SECONDS * 1000).start()
    IOLoop.current().start()

# To dos:
# Dockerize the application
# Add sys argv to enable changing the image request frequency

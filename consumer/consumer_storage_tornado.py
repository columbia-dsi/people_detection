from PIL import Image
from io import BytesIO
import pickle
import json
import numpy as np
from pykafka import KafkaClient
from pykafka.common import OffsetType
import requests
import os
from tornado import gen, httpserver, ioloop, log, web
import random
import time


class MainHandler(web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.write(prediction_json)


def gen_client(hosts="127.0.0.1:9092", topic_name='people-detection'):
    client = KafkaClient(hosts=hosts)
    topic = client.topics[topic_name]
    return client, topic


def decode(msg):
    msg = pickle.loads(msg)
    return msg


def model(msg):
    """Call the model from here maybe"""
    url = 'https://southcentralus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/\
    eff56ac8-0f36-41d9-93a9-da19396b0f30/detect/iterations/Iteration2_ppl_focus/image'
    headers = {
        'Prediction-Key': os.getenv('AZURE_VIS_KEY'),
        'Content-Type': 'application/octet-stream'
    }
    r = requests.post(url=url, headers=headers, data=msg['img'])
    predictions = r.json()
    print('Number of object predictions: {}'.format(
        len(predictions['predictions'])))
    print('Frame Number:', msg['frame_num'],
          'Image Dimensions:', np.array(Image.open(BytesIO(msg['img']))).shape)
    return len(predictions['predictions'])


@gen.coroutine
def get_prediction():
    # Using prediction_json as a global variable that is returned when a request is made to the tornado app
    # Update logic here to assign to prediction_json the XY coords (or any other data) required to be returned
    global prediction_json
    while True:
        for msg in consumer:
            yield print("Getting Prediction")
            if msg is not None:
                msg = decode(msg.value)
                print("Calling the vision API")
                pred_len = model(msg)
                prediction_json = {'num_of_predictions': pred_len}
            # The sleep time should be equal to or larger than the produce time
            yield gen.sleep(30)


def make_app():
    return web.Application([
        (r"/", MainHandler)
    ],
        debug=False)


def main():
    app = make_app()
    # start server
    server = httpserver.HTTPServer(app)
    server.listen(8080)

    ioloop.IOLoop.instance().spawn_callback(get_prediction)
    io_loop = ioloop.IOLoop.instance()

    print('starting ioloop')
    io_loop.start()


if __name__ == "__main__":
    client, topic = gen_client(
        hosts="127.0.0.1:9092", topic_name='people-detection')
    consumer = topic.get_simple_consumer(fetch_message_max_bytes=104857600)
    main()


# To dos:
# Dockerize the application
# Improve the consumer - just return the last unconsumed message in a non-blocking manner

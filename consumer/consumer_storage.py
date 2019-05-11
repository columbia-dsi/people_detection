from PIL import Image
from io import BytesIO
import pickle
import json
import numpy as np
from pykafka import KafkaClient
from pykafka.common import OffsetType
import requests
import os

PREDICTION_DIR_PATH = '/Users/harish/IdeaProjects/datascience_certification/data_analytics_pipeline/project/prediction'


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
    print("Calling the vision API")
    r = requests.post(url=url, headers=headers, data=msg['img'])
    predictions = r.json()
    prediction_json = {'num_of_predictions': len(predictions['predictions'])}
    pickle.dump(prediction_json, open(
        '{}/pred.pickle'.format(PREDICTION_DIR_PATH), 'wb'))
    print('Number of object predictions: {}'.format(
        len(predictions['predictions'])))
    print('Frame Number:', msg['frame_num'],
          'Image Dimensions:', np.array(Image.open(BytesIO(msg['img']))).shape)


if __name__ == "__main__":
    client, topic = gen_client(
        hosts="127.0.0.1:9092", topic_name='people-detection')
    consumer = topic.get_simple_consumer(fetch_message_max_bytes=104857600)
    for msg in consumer:
        print("Receiving Message")
        if msg is not None:
            msg = decode(msg.value)
            model(msg)


# To dos:
# Dockerize the application
# Improve the consumer - currently it is a simple consumer

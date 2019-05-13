from PIL import Image
from io import BytesIO
import pickle
import json
import numpy as np
from pykafka import KafkaClient
from pykafka.common import OffsetType
import requests
import os
import sys
import pandas as pd

PREDICTION_DIR_PATH = '/Users/harish/IdeaProjects/datascience_certification/data_analytics_pipeline/project/prediction'


def gen_client(hosts="127.0.0.1:9092", topic_name='people-detection'):
    client = KafkaClient(hosts=hosts)
    topic = client.topics[topic_name]
    return client, topic


def decode(msg):
    msg = pickle.loads(msg)
    return msg


def Bbox(predictions):
    df = pd.DataFrame(predictions['predictions'])
    df1 = pd.DataFrame(dict(df['boundingBox'])).T
    df1['right'] = df1['left'] + df1['width']
    df1['bottom'] = df1['top'] - df1['height']
    df = df1.merge(df['probability'], right_index=True, left_index=True)
    left_most = min(df['left'])
    # right_most = max(df['left']) + df.loc[df['left'] == max(df['left']), 'width'].iloc[0]
    # bottom_most = min(df['top'])
    top_most = max(df['top']) + df.loc[df['top']
                                       == max(df['top']), 'height'].iloc[0]
    height_avg = df['height'].mean()
    width_avg = df['width'].mean()
    nrows = 5
    ncols = 9
    mat = np.zeros((nrows, ncols))
    for i in range(nrows):
        for j in range(ncols):
            top_n = top_most - i * (height_avg)
            bottom_n = top_most - (i + 1) * height_avg
            left_n = left_most + j * width_avg
            right_n = left_most + (j + 1) * width_avg
            mat[i][j] = (df['probability'].loc[(((df['top'] <= top_n) & (df['top'] >= bottom_n))
                                                | ((df['bottom'] <= top_n) & (df['bottom'] >= bottom_n)))
                                               | (((df['right'] <= right_n) & (df['right'] >= left_n)) |
                                                ((df['left'] <= right_n) & (df['left'] >= left_n)))]).mean()
    return mat.tolist()


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
    pred_len = len(predictions['predictions'])
    XY_coords = Bbox(predictions)
    prediction_json = {'num_of_predictions': pred_len,
                       'Coords_with_prob': XY_coords}
    pickle.dump(prediction_json, open(
        '{}/pred.pickle'.format(PREDICTION_DIR_PATH), 'wb'))
    print('Frame Number:', msg['frame_num'],
          'Image Dimensions:', np.array(Image.open(BytesIO(msg['img']))).shape)
    print('Number of object predictions: {}'.format(
        pred_len))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        PREDICTION_DIR_PATH = int(sys.argv[1])

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

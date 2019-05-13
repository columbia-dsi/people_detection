from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import distutils.util
import os
import sys
import asyncio
import pickle.loads
import json.dumps
from collections import defaultdict
from tornado.web import RequestHandler, Application
from tornado.ioloop import IOLoop, PeriodicCallback

from pykafka import KafkaClient

import torch
from PIL import Image
from io import BytesIO
import numpy as np

import _init_paths
import nn
from core.config import cfg, cfg_from_file, assert_and_infer_cfg
from core.test import im_detect_all
from modeling.model_builder import Generalized_RCNN
import datasets.dummy_datasets as datasets
import utils.misc as misc_utils
import utils.net as net_utils
import utils.vis as vis
from utils.timer import Timer

INFER_SLEEP = 10

def load_model(config_path, checkpoint_path, dataset):
    # Load the coco dataset
    cfg.MODEL.NUM_CLASSES = len(dataset.classes)

    # Load a configuration file
    cfg_from_file(config_path)
    cfg.MODEL.LOAD_IMAGENET_PRETRAINED_WEIGHTS = False  # Don't need to load imagenet pretrained weights
    assert_and_infer_cfg()

    # Load the model from a checkpoint
    maskRCNN = Generalized_RCNN()
    maskRCNN.cuda()
    checkpoint = torch.load(checkpoint_path, map_location = lambda storage, loc: storage)
    net_utils.load_ckpt(maskRCNN, checkpoint['model'])
    maskRCNN = nn.DataParallel(maskRCNN, cpu_keywords=['im_info', 'roidb'], minibatch=True, device_ids=[0])
    maskRCNN.eval()

    return maskRCNN

# POST an image for prediction
'''
class PredictHandler(RequestHandler):
    def post(self):
        boxes, segms, keyps, classes = self.predict()
        sorted_idx = np.argsort(-(boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1]))
        class_names = [vis.get_class_string(classes[i], boxes[i, -1], self.application.dataset) for i in sorted_idx]
        #self.write(f'{boxes}\n{segms}\n{keyps}\n{classes}')
        self.write({'classes':class_names})

    def predict(self):
        img = Image.open(BytesIO(self.request.files['img'][0]['body']))
        timers = defaultdict(Timer)
        pred = im_detect_all(self.application.model, np.asarray(img), timers = timers)
        converted = vis.convert_from_cls_format(*pred)
        return converted
'''

class PredictHandler(RequestHandler):
    def get(self):
        if self.application.pred is None:
            return

        boxes, segms, keyps, classes = self.application.pred
        sorted_idx = np.argsort(-(boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1]))
        class_names = [vis.get_class_string(classes[i], boxes[i, -1], self.application.dataset) for i in sorted_idx]
        
        # Convert (x0, y0, w, h) to (x0, y0, x1, y1) representing bottom left
        # and top right corner respectively.
        boxes[:, 2] = boxes[:, 0] + boxes[:, 2]
        boxes[:, 3] = boxes[:, 1] + boxes[:, 3]

        response = json.dumps({'classes': class_names, 'boxes': boxes})
        self.write(response)

class ModelApplication(Application):
    def __init__(self, handler_mapping, config, checkpoint):
        self.dataset = datasets.get_coco_dataset() # Load the coco dataset
        self.model = load_model(config, checkpoint, self.dataset)
        self.client = KafkaClient(hosts = '127.0.0.1:9092')
        self.topic = self.client.topics['people-detection']
        self.consumer = self.topic.get_simple_consumer(fetch_message_max_bytes = 104857600)
        self.pred = None
        super(ModelApplication, self).__init__(handler_mapping, debug = True)

    async def predict(self):
        while True:
            msg = self.consumer.consume()
            msg = pickle.loads(msg)
            img = Image.open(BytesIO(msg['img']))

            pred = im_detect_all(self.model, np.asarray(img), timers = defaultdict(Timer))
            self.pred = vis.convert_from_cls_format(*pred)

            await asyncio.sleep(INFER_SLEEP)

if __name__ == '__main__':
    if not torch.cuda.is_available():
        sys.exit("Need a CUDA device to run the code.")

    checkpoint = 'panet.pth'
    config = './config/e2e_panet_R-50-FPN_2x_mask.yaml'
    handler_mapping = [
                       (r'/predict', PredictHandler),
                      ]
    application = ModelApplication(handler_mapping, config, checkpoint)
    application.listen(8080)
    IOloop.current().spawn_callback(application.predict)
    IOLoop.current().start()
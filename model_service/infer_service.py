from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import distutils.util
import os
import sys
from collections import defaultdict
from tornado.web import RequestHandler, Application
from tornado.ioloop import IOLoop, PeriodicCallback

import torch
from PIL import Image
from io import StringIO, BytesIO
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

def load_model(config_path, checkpoint_path):
    # load coco dataset
    dataset = datasets.get_coco_dataset()
    cfg.MODEL.NUM_CLASSES = len(dataset.classes)

    # load config file
    cfg_from_file(config_path)
    cfg.MODEL.LOAD_IMAGENET_PRETRAINED_WEIGHTS = False  # Don't need to load imagenet pretrained weights
    assert_and_infer_cfg()

    # load model from checkpoint
    maskRCNN = Generalized_RCNN()
    maskRCNN.cuda()

    checkpoint = torch.load(checkpoint_path, map_location = lambda storage, loc: storage)
    net_utils.load_ckpt(maskRCNN, checkpoint['model'])

    maskRCNN = nn.DataParallel(maskRCNN, cpu_keywords=['im_info', 'roidb'], minibatch=True, device_ids=[0])
    maskRCNN.eval()

    return maskRCNN

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

class ModelApplication(Application):
    def __init__(self, handler_mapping, config, checkpoint):
        self.dataset = datasets.get_coco_dataset()
        self.model = load_model(config, checkpoint)
        super(ModelApplication, self).__init__(handler_mapping, debug = True)

if __name__ == '__main__':
    if not torch.cuda.is_available():
        sys.exit("Need a CUDA device to run the code.")

    checkpoint = 'panet.pth'
    config = './config/e2e_panet_R-50-FPN_2x_mask.yaml'
    handler_mapping = [
                       (r'/predict', PredictHandler),
                      ]
    application = ModelApplication(handler_mapping, config, checkpoint)
    application.listen(7777)
    IOLoop.current().start()

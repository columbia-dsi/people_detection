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

import _init_paths
import nn
from core.config import cfg, cfg_from_file, assert_and_infer_cfg
from core.test import im_detect_all
from modeling.model_builder import Generalized_RCNN
import datasets.dummy_datasets as datasets
import utils.misc as misc_utils
import utils.net as net_utils
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
        cls_boxes, cls_segms, cls_keyps = self.predict()
        self.write(f'{cls_boxes}\n{cls_segms}\n{cls_keyps}')

    def predict(self, img):
        img = cv2.imread(self.request.body)
        timers = defaultdict(Timer)
        return im_detect_all(self.application.model, img, timers = timers)

class ModelApplication(Application):
    def __init__(self, handler_mapping, config, checkpoint):
        self.model = load_model(config, checkpoint)
        super(ModelApplication, self).__init__(handler_mapping)

if __name__ == '__main__':
    if not torch.cuda.is_available():
        sys.exit("Need a CUDA device to run the code.")

    checkpoint = 'panet.pth'
    config = 'e2e_panet_R-50-FPN_2x_mask.yaml'
    handler_mapping = [
                       (r'/predict', PredictHandler),
                      ]
    application = ModelApplication(handler_mapping)
    application.listen(7777)
    IOLoop.current().start()
"""Add {PROJECT_ROOT}/lib. to PYTHONPATH

Usage:
import this module before import any modules under lib/
e.g 
    import _init_paths
    from core.config import cfg
""" 

import os.path as osp
import sys

def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)

this_dir = osp.abspath(osp.dirname(__file__))

# Add lib to PYTHONPATH
lib_path = osp.join(this_dir, 'lib')
cfg_path = osp.join(this_dir, 'config')
ckpt_path = osp.join(this_dir, 'checkpoint')
add_path(lib_path)

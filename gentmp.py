#author: johnxguo
#date: 2018-11-21

import json
import os
import sys 
from tools.tmpgenerator import GenTmpVlst

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.loads(f.read())
    tmppath = config['workpath'] + 'tmp/'
    vlst = sys.path[0] + '/tmp.vlst'
    GenTmpVlst(tmppath, vlst)
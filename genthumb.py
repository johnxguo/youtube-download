#author: johnxguo
#date: 2019-4-14

import json
import os
import sys 
from tools.thumbnail import ThumbnailCmd

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.loads(f.read())
    workpath = config['workpath']
    ThumbnailCmd([sys.argv[0], workpath, sys.argv[1]])
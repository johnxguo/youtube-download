#author: johnxguo
#date: 2019-4-13

import json
import os
import sys 

ids = {*()}

files = os.listdir('.')
for filename in files:
    if os.path.isfile(filename) and filename.endswith('webm'):
        v = filename[filename.rfind(' - ') + 3 : filename.rfind('.')]
        print(v)
        ids.add(v)

lines = []
with open('1', 'r', encoding='utf-8') as f:
    lines = f.readlines()

m = [x for x in lines if x.strip('\n') not in ids]

with open('donelist', 'w', encoding='utf-8') as f:
    for _id in m:
        f.write(_id)
        print(_id)
    
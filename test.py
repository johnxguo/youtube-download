#author: johnxguo
#date: 2018-10-28

import os
import time
from colorama import Fore, Back, Style, init

import asyncio

def asyncrun(future):
    return asyncio.get_event_loop().run_until_complete(future)

async def fa(num):
    a = 1 / num
    

async def downloadPath(path):
    tasks = [
        asyncio.ensure_future(fa(1)),
        asyncio.ensure_future(fa(0))
    ]
    try:
        a = await asyncio.wait(tasks)
        a = await fa(0)
    except Exception as err:
        print(err)

print(0)
a = asyncrun(downloadPath(1))
print(1)
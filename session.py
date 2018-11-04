#author: johnxguo
#date: 2018-10-31

import os
import aiohttp
import asyncio
import time
from speed import SpeedHelper

class Session:
    def __init__(self, cookies, headers):
        self.cacheSize = 3000000
        self.chuckSize = 1000000
        self.proxy = 'http://127.0.0.1:1080'
        self.session = asyncio.get_event_loop().run_until_complete(self.create_session(cookies, headers))

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(self.session.close())

    async def create_session(self, cookies, headers):
        return aiohttp.ClientSession(cookies=cookies, headers=headers, timeout=aiohttp.ClientTimeout(total=100000))

    async def get(self, url:str):
        async with self.session.get(url, proxy=self.proxy) as rsp:
            return await rsp.text()

    async def fetch(self, url:str, path:str, handler:callable = None):
        with open(path, 'wb') as file:
            async with self.session.get(url, proxy=self.proxy) as rsp:
                speedHelper = SpeedHelper(90, int(rsp.headers["Content-Length"]))
                counter = 0
                cache = bytes()
                lastsize = 0
                while 1:
                    chuck = await rsp.content.read(self.chuckSize)
                    if not chuck:
                        file.write(cache)
                        break
                    cache = cache + chuck
                    if len(cache) > self.cacheSize:
                        file.write(cache)
                        cache = bytes()
                    counter = counter + 1
                    speedHelper.mark(len(chuck))
                    if counter % 100 == 0:
                        if handler:
                            size = speedHelper.size_done() - lastsize
                            lastsize = speedHelper.size_done()
                            handler(url, path, size, speedHelper.size_all(), speedHelper.size_done(), speedHelper.speed())

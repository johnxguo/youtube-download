#author: johnxguo
#date: 2018-10-31

import os
import aiohttp
import asyncio
import time
from .speed import SpeedHelper

class Session:
    def __init__(self, cookies, headers, proxy = None):
        self.cacheSize = 3000000
        self.chuckSize = 1000000
        self.cookies = cookies
        self.headers = headers
        self.proxy = proxy
        self.session = asyncio.get_event_loop().run_until_complete(self.create_session(cookies, headers))

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(self.session.close())

    async def create_session(self, cookies, headers):
        return aiohttp.ClientSession(cookies=cookies, headers=headers, timeout=aiohttp.ClientTimeout(total=100000))

    async def get(self, url:str):
        async with self.session.get(url, proxy=self.proxy) as rsp:
            return await rsp.text()
    
    async def getWithHeaders(self, url:str, headers):
        headers = {**self.headers, **headers} 
        async with self.session.get(url, proxy=self.proxy, headers=headers) as rsp:
            return await rsp.text()

    async def fetch(self, url:str, path:str, handler:callable = None):
        tmpPath = path + '.tmp'
        startsize = 0
        try:
            if os.path.exists(path):
                return True
            if os.path.exists(tmpPath):
                startsize = os.path.getsize(tmpPath)
            with open(tmpPath, 'wb' if startsize==0 else 'ab') as file:
                headers = self.headers if startsize == 0 else {**self.headers, 'Range':f'bytes={startsize}-'}
                async with self.session.get(url, proxy=self.proxy, headers=headers, verify_ssl=False) as rsp:
                    speedHelper = SpeedHelper(90, int(rsp.headers["Content-Length"]))
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
                        speedHelper.mark(len(chuck))
                        if handler:
                            size = speedHelper.size_done() - lastsize
                            lastsize = speedHelper.size_done()
                            handler(url, path, size, speedHelper.size_all() + startsize, speedHelper.size_done() + startsize, speedHelper.speed())
            size = os.path.getsize(tmpPath)
            if size > 0:
                os.rename(tmpPath, path)
                return True
            return False
        except Exception as err:
            print(err)
            return False
        finally:
            if os.path.exists(tmpPath):
                if os.path.getsize(tmpPath) == 0:
                    os.remove(tmpPath)


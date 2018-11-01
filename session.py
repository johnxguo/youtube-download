#author: johnxguo
#date: 2018-10-31

import os
import aiohttp
import asyncio
import time

class Session:
    def __init__(self, cookies, headers):
        self.proxy = 'http://127.0.0.1:1080'
        self.session = asyncio.get_event_loop().run_until_complete(self.create_session(cookies, headers))

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(self.session.close())

    async def create_session(self, cookies, headers):
        return aiohttp.ClientSession(cookies=cookies, headers=headers)

    async def get(self, url:str):
        async with self.session.get(url, proxy=self.proxy) as rsp:
            return await rsp.text()

    async def fetch(self, url:str, path:str):
        with open(path, 'wb') as file:
            async with self.session.get(url, proxy=self.proxy) as rsp:
                st = time.time()
                counter = 0
                u = 1024*1024*5
                while 1:
                    chuck = await rsp.content.read(u)
                    if not chuck:
                        break
                    file.write(chuck)
                    counter = counter + 1
                    dis = time.time() - st + 1
                    size = counter * 5
                    print(str(size / dis) + " M/s, " + str(size))

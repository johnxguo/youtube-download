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
                size_all = rsp.headers["Content-Length"]
                size_done = 0
                time_st = time.time()
                speedqueue = [{'time':time_st, 'size': 0}]
                speedSize = 20
                cache = bytes()
                filename = os.path.split(path)[1]
                purename = filename[filename.find('-', filename.find('-') + 1) + 2:]
                logname = purename
                if len(logname) > 34:
                    logname = logname[:15] + '...' + logname[-19:]
                while 1:
                    chuck = await rsp.content.read(1000000)
                    if not chuck:
                        file.write(cache)
                        break
                    size_done += len(chuck)
                    cache = cache + chuck
                    if len(cache) > 3000000:
                        file.write(cache)
                        cache = bytes()
                    speedqueue.append({'time':time.time(), 'size':size_done})
                    log = logname + ' | ' + self.sizeByte2Str(size_done) + '/' + self.sizeByte2Str(int(size_all))
                    if len(speedqueue) > speedSize:
                        sizediff = speedqueue[-1]['size'] - speedqueue[0]['size']
                        timediff = speedqueue[-1]['time'] - speedqueue[0]['time']
                        speed = sizediff / timediff
                        log = log + ' | ' + self.sizeByte2Str(speed) + '/s'
                        speedqueue.pop(0)
                    print(log)

    def sizeByte2Str(self, size):
        if size > 1024*1024:
            return "%.2f"%(size / (1024 * 1024)) + 'M'
        else:
            return "%.2f"%(size / 1024) + 'K'
                
                        
                    

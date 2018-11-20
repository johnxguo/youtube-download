#author: johnxguo
#date: 2018-11-7

import asyncio
from login.youtube import YoutubeLoginHelper
from .session import Session

class YoutubeSession:
    def __init__(self, username = None, password = None, proxy = None):
        headers = {
            'Connection':'keep-alive',
            'user-agent' : 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'referer' : 'https://www.youtube.com/'
        }
        self.username = username
        self.password = password
        if password:
            cookies = YoutubeLoginHelper(username, password).login().getCookie()
            self.session = Session(cookies, headers, proxy)
            self.username = username if cookies else None
        elif not username:
            self.session = Session(None, headers, proxy)
            self.username = 'nobody'

    async def get(self, url:str):
        return await self.session.get(url)

    async def getWithHeaders(self, url:str, headers):
        return await self.session.getWithHeaders(url, headers)

    async def fetch(self, url:str, path:str, handler:callable = None):
        return await self.session.fetch(url, path, handler)

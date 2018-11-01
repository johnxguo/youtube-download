#author: johnxguo
#date: 2018-10-31

import os
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
from urllib.parse import parse_qs
from login.youtube import YoutubeLoginHelper
from session import Session
import asyncio

class YoutubeSession:
    def __init__(self):
        headers = {
            'Connection':'keep-alive',
            'user-agent' : 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'referer' : 'https://www.youtube.com/'
        }

        with open('user.json', 'r') as f:
            username = f.readline().strip()
            password = f.readline().strip()
        param = (username, password) if password else self.inputUserInfo()
        cookies = YoutubeLoginHelper(*param).login().getCookie() 
        self.session = Session(cookies, headers)

    def inputUserInfo(self):
        return input('username:'), input('password:')

    async def get(self, url:str):
        return await self.session.get(url)

    async def fetch(self, url:str, path:str):
        return await self.session.fetch(url, path)


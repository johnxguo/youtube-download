#author: johnxguo
#date: 2018-10-31

import os
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
from urllib.parse import parse_qs
from login.youtube import YoutubeLoginHelper
from session import Session
import asyncio
import json
from enum import Enum, unique

def logfile(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        print (content, file = f)

class YoutubeSession:
    def __init__(self, needlogin = True):
        headers = {
            'Connection':'keep-alive',
            'user-agent' : 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'referer' : 'https://www.youtube.com/'
        }

        if needlogin:
            username = None
            password = None
            if os.path.isfile('user.json'):
                with open('user.json', 'r') as f:
                    username = f.readline().strip()
                    password = f.readline().strip()
            param = (username, password) if password else self.inputUserInfo()
            (username, password) = param
            cookies = YoutubeLoginHelper(*param).login().getCookie()
            self.session = Session(cookies, headers)
            self.username = username if cookies else None
        else:
            self.session = Session(None, headers)
            self.username = 'nobody'

    def inputUserInfo(self):
        return input('username:'), input('password:')

    async def get(self, url:str):
        return await self.session.get(url)

    async def fetch(self, url:str, path:str):
        return await self.session.fetch(url, path)


class YoutubeDownloader:
    def __init__(self, session:YoutubeSession):
        self.session = session
        self.curTaskNum = 0
        self.maxTaskNum = 10
        self.prefix_v = 'https://www.youtube.com/watch?v='
        self.prefix_channel = 'https://www.youtube.com/channel/'
        self.prefix_playlist = 'https://www.youtube.com/playlist?list='
    
    async def downloadPath(self, path):
        if path == '.':
            await self.addAllSelfPlayLists()
        elif path.startswith(self.prefix_v):
            await self.addFilm(path)
        elif path.startswith(self.prefix_channel):
            await self.addChannel(path)
        elif path.startswith(self.prefix_playlist):
            await self.addPlaylist(path)
        elif os.path.splitext(path)[1] == '.vlst':
            await self.addVList(path)
        else:
            print('ignore unknown path:' + path)

    async def addAllSelfPlayLists(self):
        print('will add all your playlists..')

    async def addFilm(self, url):
        try:
            query = urlsplit(url).query
            if query:
                v = parse_qs(query)['v'][0].strip()
                if v:
                    if self.checkExist(v):
                        print('exist! v=' + v)
                        return
                    else:
                        await self.downloadV(v)
                        return
        except Exception as err:
            print(err)
        # logfile append
        print('download url fail: ' + url)

    async def addVList(self, path):
        print('will add vlist: ' + path)
        tasks = None
        with open(path, 'r') as file:
            lines = file.readlines()
            tasks = [asyncio.ensure_future(self.downloadPath(line)) for line in lines]
        if tasks:
            await asyncio.wait(tasks)

    async def addChannel(self, url):
        print('will add channel: ' + url)

    async def addPlaylist(self, url):
        print('will add playlist: ' + url)

    async def downloadV(self, v):
        print('will download v=' + v)
        while self.curTaskNum >= self.maxTaskNum:
            await asyncio.sleep(2)
        self.curTaskNum = self.curTaskNum + 1
        url_v = self.prefix_v + v
        html_v = await self.session.get(url_v)
        st_str = 'ytplayer.config = '
        config_st = html_v.find(st_str)
        if config_st == -1:
            print('get config fail, v=' + v)
            return
        config_st = config_st + len(st_str)
        config_et = html_v.find("};", config_st)
        if config_et == -1:
            print('get config fail, v=' + v)
            return
        config_et = config_et + 1
        config = html_v[config_st:config_et]
        j = json.loads(config)
        player_response = json.loads(j['args']['player_response'])
        videoDetails = player_response['videoDetails']
        formats = player_response['streamingData']['formats'] + player_response['streamingData']['adaptiveFormats']
        title = videoDetails['title']
        pureTitle = self.removeInvalidFilenameChars(title)
        channel = videoDetails['channelId']
        filename = channel + ' - ' + v + ' - ' + pureTitle
        maxVideo = None
        maxAudio = None
        for fmt in formats:
            mediaType = None
            if fmt['mimeType'].startswith('video/webm'):
                mediaType = 'vwebm'
            if fmt['mimeType'].startswith('audio/webm'):
                mediaType = 'awebm'
            if not mediaType:
                continue
            if mediaType == 'vwebm':
                if not maxVideo:
                    maxVideo = fmt
                else:
                    try:
                        pixel_o = maxVideo['width'] * maxVideo['height']
                        pixel_t = fmt['width'] * fmt['height']
                        br_o = maxVideo['bitrate']
                        br_t = fmt['bitrate']
                        if pixel_o < pixel_t:
                            maxVideo = fmt
                        elif pixel_o == pixel_t:
                            maxVideo = maxVideo if br_o > br_t else fmt
                    except Exception as err:
                        print(err)
            if mediaType == 'awebm':
                if not maxAudio:
                    maxAudio = fmt
                else:
                    try:
                        br_o = maxAudio['bitrate']
                        br_t = fmt['bitrate']
                        maxAudio = maxAudio if br_o > br_t else fmt
                    except Exception as err:
                        print(err)
        filenameVideo = filename + '-video.webm'
        filenameAudio = filename + '-audio.webm'
        filenameMerge = filename + '.webm'
        tasks = [
            asyncio.ensure_future(self.session.fetch(maxVideo['url'], filenameVideo)),
            asyncio.ensure_future(self.session.fetch(maxAudio['url'], filenameAudio))
        ]
        await asyncio.wait(tasks)
        mergeCmd = 'ffmpeg -loglevel quiet -i \"' + filenameAudio + '\" -i \"' + filenameVideo + '\" -acodec copy -vcodec copy \"' + filenameMerge + '\"'
        print(mergeCmd)
        os.system(mergeCmd)
        os.remove(filenameAudio)
        os.remove(filenameVideo)
        self.markDownloaded(v)
        
    def checkExist(self, v):
        try:
            with open('donelist.vlst', 'r') as file:
                return (v + '\n') in file.readlines()
        except Exception as err:
            print(err)
        return False

    def markDownloaded(self, v):
        try:
            with open('donelist.vlst', 'a') as file:
                file.write(v + '\n')
        except Exception as err:
            print(err)

    def removeInvalidFilenameChars(self, filename):
        return filename.translate(str.maketrans('','',r'\/:*?"<>|'))

def asyncrun(future):
    asyncio.get_event_loop().run_until_complete(future)

session = YoutubeSession()
if not session.username:
    print('init failed! will exit.')
    exit()

downloader = YoutubeDownloader(session)

print("I'm ready!")

while 1:
    cmd = input(session.username + ">")
    cmd = cmd.strip()
    if cmd == '' or cmd == None:
        continue
    if cmd == 'exit':
        break
    elif cmd[:3] == 'dl ':
        path = cmd[3:]
        asyncrun(downloader.downloadPath(path))
        
    else:
        print("no such command!")

print("end")
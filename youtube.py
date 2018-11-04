#author: johnxguo
#date: 2018-10-31

import os
import asyncio
import json
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
from urllib.parse import parse_qs
from login.youtube import YoutubeLoginHelper
from console_color.color_helper import ColorHelper
from session import Session
from enum import Enum, unique
from speed import SpeedHelper

# uvloop don't support windows
# import uvloop
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

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

    async def fetch(self, url:str, path:str, hander:callable = None):
        return await self.session.fetch(url, path, hander)


class YoutubeDownloader:
    def __init__(self, session:YoutubeSession):
        self.session = session
        self.curTaskNum = 0
        self.maxTaskNum = 10
        self.taskCounter = 0
        self.prefix_v = 'https://www.youtube.com/watch?v='
        self.prefix_channel = 'https://www.youtube.com/channel/'
        self.prefix_playlist = 'https://www.youtube.com/playlist?list='
        self.downloadinglist = []
        self.taskmap = {}
        self.speedHelper = SpeedHelper(5)
        self.colorPrints = [ColorHelper.print_red,
                            ColorHelper.print_green,
                            ColorHelper.print_blue,
                            ColorHelper.print_yellow,
                            ColorHelper.print_purple,
                            ColorHelper.print_cyan,
                            ColorHelper.print_white]
    
    async def downloadPath(self, path):
        if path == '.':
            await self.addAllSelfPlayLists()
            return True
        elif path.startswith(self.prefix_v):
            await self.addFilm(path)
            return True
        elif path.startswith(self.prefix_channel):
            await self.addChannel(path)
            return True
        elif path.startswith(self.prefix_playlist):
            await self.addPlaylist(path)
            return True
        elif os.path.splitext(path)[1] == '.vlst':
            await self.addVList(path)
            return True
        else:
            ColorHelper.print_red('ignore unknown path:' + path)
            return False

    async def addAllSelfPlayLists(self):
        print('will add all your playlists..')

    async def addFilm(self, url):
        try:
            v = self.getV(url)
            if v:
                if self.canDownload(v):
                    await self.downloadV(v)
                    return
                else:
                    ColorHelper.print_yellow('exist! v=' + v)
                    return
        except Exception as err:
            self.logfile(err)
        self.logfile('download url fail: ' + url)

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
        self.markDownloading(v)
        print('will download v=' + v)
        while self.curTaskNum >= self.maxTaskNum:
            await asyncio.sleep(2)
        self.curTaskNum = self.curTaskNum + 1
        try:
            url_v = self.prefix_v + v
            html_v = await self.session.get(url_v)
            st_str = 'ytplayer.config = '
            config_st = html_v.find(st_str)
            if config_st == -1:
                ColorHelper.print_red('get config fail, v=' + v)
                return
            config_st = config_st + len(st_str)
            config_et = html_v.find("};", config_st)
            if config_et == -1:
                ColorHelper.print_red('get config fail, v=' + v)
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
            filename = channel + ' - ' + pureTitle + ' - ' + v
            maxVideo = {}
            maxAudio = {}
            for fmt in formats:
                mediaType = None
                if fmt['mimeType'].startswith('video/webm'):
                    mediaType = 'vwebm'
                if fmt['mimeType'].startswith('audio/webm'):
                    mediaType = 'awebm'
                if not mediaType:
                    continue
                if mediaType == 'vwebm':
                    if not bool(maxVideo):
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
                            ColorHelper.print_red(err) 
                if mediaType == 'awebm':
                    if not bool(maxAudio):
                        maxAudio = fmt
                    else:
                        try:
                            br_o = maxAudio['bitrate']
                            br_t = fmt['bitrate']
                            maxAudio = maxAudio if br_o > br_t else fmt
                        except Exception as err:
                            ColorHelper.print_red(err)  
            filenameVideo = filename + '-video.webm'
            filenameAudio = filename + '-audio.webm'
            filenameMerge = filename + '.webm'
            videoUrl = maxVideo['url']
            audioUrl = maxAudio['url']
            tasks = [
                asyncio.ensure_future(self.session.fetch(videoUrl, filenameVideo, self.fetchHander)),
                asyncio.ensure_future(self.session.fetch(audioUrl, filenameAudio, self.fetchHander))
            ]
            try:
                self.taskmap[videoUrl] = self.taskCounter
                self.taskCounter = self.taskCounter + 1
                self.taskmap[audioUrl] = self.taskCounter
                self.taskCounter = self.taskCounter + 1
                await asyncio.wait(tasks)
                mergeCmd = 'ffmpeg -loglevel quiet -i \"' + filenameAudio + '\" -i \"' + filenameVideo + '\" -acodec copy -vcodec copy \"' + filenameMerge + '\"'
                ColorHelper.print_purple('merging audio and video..')
                os.system(mergeCmd)
                os.remove(filenameAudio)
                os.remove(filenameVideo)
                self.markDownloaded(v)
                self.taskmap.pop(videoUrl)
                self.taskmap.pop(audioUrl)
                ColorHelper.print_green(filenameMerge + ' is done')
            except Exception as err:
                ColorHelper.print_red(err)
        finally:
            self.markNotDownloading(v)
            self.curTaskNum = self.curTaskNum - 1

    def getV(self, url):
        query = urlsplit(url).query
        return parse_qs(query)['v'][0].strip()
        
    def isExist(self, v):
        try:
            with open('youtube.donelist', 'r') as file:
                return (v + '\n') in file.readlines()
        except Exception as err:
            ColorHelper.print_red(err)
        return False

    def markDownloaded(self, v):
        try:
            with open('youtube.donelist', 'a') as file:
                file.write(v + '\n')
        except Exception as err:
            ColorHelper.print_red(err)

    def isDownloading(self, v):
        return v in self.downloadinglist

    def markDownloading(self, v):
        if v in self.downloadinglist:
            return
        self.downloadinglist.append(v)

    def markNotDownloading(self, v):
        if v in self.downloadinglist:
            self.downloadinglist.remove(v)

    def canDownload(self, v):
        return (not self.isExist(v)) and (not self.isDownloading(v))
    
    def removeInvalidFilenameChars(self, filename):
        return filename.translate(str.maketrans('','',r'\/:*?"<>|'))

    def logfile(self, content, pr = True):
        if pr:
            print(content)
        with open('youtube.log', 'a') as f:
            f.write(content + '\n')

    def fetchHander(self, url, path, size, size_all, size_done, speed):
        self.speedHelper.mark(size)
        colorPrint = self.colorPrints[self.urlIndex(url) % len(self.colorPrints)]
        filename = os.path.split(path)[1]
        purename = filename[filename.find(' - ') + 3 : filename.rfind(' - ')] + filename[filename.rfind('-'):]
        logname = purename 
        namelength = 60
        hlength = int(len(logname))
        counter = 3
        while self.halfWidthLen(logname) > namelength - 2:
            logname = logname[:hlength - counter] + '...' + logname[-hlength + counter:]
            counter = counter + 1
        logname = logname + ' '*(namelength - self.halfWidthLen(logname))
        ColorHelper.print_blue('downloading | ', False)
        log = logname + ' | ' + '%8s' % self.sizeByte2Str(size_done) + ' /' + '%8s' % self.sizeByte2Str(int(size_all)) + ' | ' + self.sizeByte2Str(speed) + '/s'
        colorPrint(log, False)
        ColorHelper.print_purple(' | ', False)
        allSpeedLog = self.sizeByte2Str(self.speedHelper.speed()) + '/s'
        ColorHelper.print_yellow(allSpeedLog)

    def halfWidthLen(self, s:str):
        length = len(s)
        utf8_length = len(s.encode('utf-8'))
        length = (utf8_length - length) / 2 + length
        return int(length)

    def urlIndex(self, url):
        try:
            if url in self.taskmap.keys():
                return self.taskmap[url]
            else:
                return -1
        except Exception:
            return -1
    
    def sizeByte2Str(self, size):
        if size > 1024*1024:
            return "%5.2f" % (size / (1024 * 1024)) + 'M'
        else:
            return "%5d" % (size / 1024) + 'K'

def asyncrun(future):
    return asyncio.get_event_loop().run_until_complete(future)

session = YoutubeSession(False)
if not session.username:
    ColorHelper.print_red('init failed! will exit.')
    exit()

downloader = YoutubeDownloader(session)

ColorHelper.print_green("I'm ready!")

while 1:
    cmd = input(session.username + ">")
    cmd = cmd.strip()
    if cmd == '' or cmd == None:
        continue
    if cmd == 'exit':
        break
    elif cmd[:3] == 'dl ':
        path = cmd[3:]
        # uvloop
        asyncrun(downloader.downloadPath(path))
    else:
        if not asyncrun(downloader.downloadPath(cmd)):
            ColorHelper.print_red("no such command!")

print("end")
#author: johnxguo
#date: 2018-11-7

import os
import sys
import asyncio
import json
from urllib.parse import urlsplit
from urllib.parse import parse_qs
from console_color.color_helper import ColorHelper
from youtubesession import YoutubeSession
from enum import Enum, unique
from speed import SpeedHelper

class YoutubeDownloader:
    def __init__(self, session:YoutubeSession):
        self.session = session
        self.curTaskNum = 0
        self.maxTaskNum = 5
        self.taskCounter = 0
        self.maxTaskCounter = sys.maxsize
        self.workpath = './'
        self.donefile = './youtube.donelist'
        self.logsfile = './youtube.log'
        self.stopfile = './stop'
        self.prefix_v = 'https://www.youtube.com/watch?v='
        self.prefix_channel = 'https://www.youtube.com/channel/'
        self.prefix_playlist = 'https://www.youtube.com/playlist?list='
        self.continueurl = r'https://www.youtube.com/browse_ajax?ctoken=%s&continuation=%s&itct=%s'
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
    
    def setMaxTaskNum(self, maxTaskNum):
        self.maxTaskNum = maxTaskNum
        return self

    def setWorkPath(self, workpath):
        self.workpath = workpath
        return self
    
    def setMaxTaskCounter(self, maxTaskCounter):
        self.maxTaskCounter = maxTaskCounter
        return self

    def setDonefile(self, donefile):
        self.donefile = donefile
        return self

    def setLogsfile(self, logsfile):
        self.logsfile = logsfile
        return self
    
    def setStopfile(self, stopfile):
        self.stopfile = stopfile
        return self

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
        # include playlists, subscribed channels, and mixs

    async def addFilm(self, url):
        if url.find('list=') != -1:
            await self.addMix(url)
        try:
            v = self.getV(url)
            if v:
                if self.canDownload(v):
                    if await self.downloadV(v):
                        return
                else:
                    ColorHelper.print_yellow('exist! v=' + v)
                    return
        except Exception as err:
            self.logfile(err)
        self.logfile('download url fail: ' + url[:-1])

    async def addMix(self, url):
        print('will add mix: ' + url)
        # gethtml2

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
        # all videos is actually a playlist
        # other playlists, merge

    async def addPlaylist(self, url):
        url = url.strip()
        print('will add playlist: ' + url)
        html = await self.session.get(url)
        try:
            info = self.getConfigFromHtml2(html)
            contiHeaders = {}
            try:
                contiHeaderInfo = self.getConfigFromHtml3(html)
                contiHeaders = self.getContiRequestHeaders(contiHeaderInfo)
            except Exception:
                ColorHelper.print_blue('no more')
            contents = await self.processPlaylistInfo(info, contiHeaders)
            vids = [videoinfo['playlistVideoRenderer']['videoId'] for videoinfo in contents]
            ColorHelper.print_yellow(url + ' | total videos:' + str(len(vids)))
            tasks = [asyncio.ensure_future(self.downloadV(vid)) for vid in vids]
            await asyncio.wait(tasks)
        except Exception as err:
            ColorHelper.print_red(err)
            ColorHelper.print_red('get playlist fail, url=' + url)

    async def processPlaylistInfo(self, info, contiHeaders):
        contents = info['contents']
        try:
            contiinfo = info['continuations'][0]['nextContinuationData']
            continuation = contiinfo['continuation']
            itct = contiinfo['clickTrackingParams']
            contiurl = self.continueurl % (continuation, continuation, itct)
            rsp = await self.session.getWithHeaders(contiurl, contiHeaders) 
            json = self.getContiResponseJson(rsp)
            info_new = json['response']['continuationContents']['playlistVideoListContinuation']
            contents = contents + await self.processPlaylistInfo(info_new, contiHeaders)
            ColorHelper.print_green('contents: ' + str(len(contents)))
        except Exception:
            ColorHelper.print_blue('no more')
            pass
        return contents

    def getContiResponseJson(self, rsp):
        j = json.loads(rsp)
        for o in j:
            if 'response' in o:
                return o
        return None

    def getContiRequestHeaders(self, info):
        headers = {
            'X-YouTube-Variants-Checksum': info['VARIANTS_CHECKSUM'],
            'X-Youtube-Identity-Token': info['ID_TOKEN'],
            'X-YouTube-Page-CL': str(info['PAGE_CL']),
            'X-YouTube-Client-Name': '1',
            'X-YouTube-Client-Version': info['INNERTUBE_CONTEXT_CLIENT_VERSION'],
            'Accept-Encoding': 'gzip, deflate, br'
        }
        return headers

    def getConfigFromHtml1(self, html):
        st_str = r'ytplayer.config = '
        et_str = r"};"
        j = self.getConfigFromHtmlBase(html, st_str, et_str)
        return json.loads(j['args']['player_response'])
    
    def getConfigFromHtml2(self, html):
        st_str = r'window["ytInitialData"] = '
        et_str = r"};"
        j = self.getConfigFromHtmlBase(html, st_str, et_str)
        return j['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']

    def getConfigFromHtml3(self, html):
        st_str = r'window.ytplayer = {};ytcfg.set('
        et_str = r"});"
        return self.getConfigFromHtmlBase(html, st_str, et_str)

    def getConfigFromHtmlBase(self, html, st_str, et_str):
        config_st = html.find(st_str)
        if config_st == -1:
            return None
        config_st = config_st + len(st_str)
        config_et = html.find(et_str, config_st)
        if config_et == -1:
            return None
        config_et = config_et + 1
        config = html[config_st:config_et]
        j = json.loads(config)
        return j

    def checkDownloadState(self, v):
        if self.taskCounter >= self.maxTaskCounter:
            ColorHelper.print_purple(r'maxTaskCounter[%d] reached! v=%s' % (self.maxTaskCounter, v))
            return False
        if not self.canDownload(v):
            ColorHelper.print_yellow('exist! v=' + v)
            return False
        if self.isStop():
            ColorHelper.print_yellow('global stop!')
            return False
        return True

    async def downloadV(self, v):
        if not self.checkDownloadState(v):
            return
        while self.curTaskNum >= self.maxTaskNum:
            await asyncio.sleep(2)
        # double check
        if not self.checkDownloadState(v):
            return
        self.markDownloading(v)
        ColorHelper.print_cyan(r' ------ begin download v=%s ------ '%(v))
        self.curTaskNum = self.curTaskNum + 1
        try:
            url_v = self.prefix_v + v
            html_v = await self.session.get(url_v)
            player_response = self.getConfigFromHtml1(html_v)
            if not player_response:
                ColorHelper.print_red('get config fail, v=' + v)
                return False
            videoDetails = player_response['videoDetails']
            formats = player_response['streamingData']['formats'] + player_response['streamingData']['adaptiveFormats']
            title = videoDetails['title']
            pureTitle = self.removeInvalidFilenameChars(title)
            channel = videoDetails['channelId']
            filename = channel + ' - ' + pureTitle + ' - ' + v
            maxAudio, maxVideo = self.getMaxAV(formats)
            if (not bool(maxAudio)) or (not bool(maxVideo)):
                ColorHelper.print_red('get avconfig fail, v=' + v)
                return False
            try:
                tmpPath = self.workpath + 'tmp/'
                if not os.path.exists(tmpPath):
                    os.makedirs(tmpPath)
                videoPath = tmpPath + filename + '-video.webm'
                audioPath = tmpPath + filename + '-audio.webm'
                outptPath = self.workpath + filename + '.webm'
                videoUrl = maxVideo['url']
                audioUrl = maxAudio['url']
                self.taskmap[videoUrl] = self.taskCounter
                self.taskCounter = self.taskCounter + 1
                self.taskmap[audioUrl] = self.taskCounter
                self.taskCounter = self.taskCounter + 1
                tasks = [
                    asyncio.ensure_future(self.session.fetch(videoUrl, videoPath, self.fetchHandler)),
                    asyncio.ensure_future(self.session.fetch(audioUrl, audioPath, self.fetchHandler))
                ]
                await asyncio.wait(tasks)
                if tasks[0].result() and tasks[1].result():
                    mergeCmd = 'ffmpeg -loglevel quiet -nostdin -y -i \"' + audioPath + '\" -i \"' + videoPath + '\" -acodec copy -vcodec copy \"' + outptPath + '\"'
                    ColorHelper.print_purple('merging audio and video..')
                    os.system(mergeCmd)
                    self.markDownloaded(v)
                    ColorHelper.print_green(outptPath + ' is done')
                else:
                    ColorHelper.print_red(r'network err! v=%s download fail!'%(v))
                self.taskmap.pop(videoUrl)
                self.taskmap.pop(audioUrl)
                os.remove(videoPath)
                os.remove(audioPath)
            except Exception as err:
                ColorHelper.print_red(err)
        except Exception as err:
            ColorHelper.print_red(err)
            ColorHelper.print_red('get avconfig fail, v=' + v)
            return False
        finally:
            self.markNotDownloading(v)
            self.curTaskNum = self.curTaskNum - 1
        return True

    def getMaxAV(self, formats):
        maxAudio, maxVideo = self.getMaxAVWithExt(formats, 'webm')
        if (not bool(maxAudio)) or (not bool(maxVideo)):
            maxAudio, maxVideo = self.getMaxAVWithExt(formats, 'mp4')
        if (not bool(maxAudio)) or (not bool(maxVideo)):
            maxAudio, maxVideo = self.getMaxAVWithExt(formats, '')
        return maxAudio, maxVideo

    def getMaxAVWithExt(self, formats, ext): 
        maxAudio = {}         
        maxVideo = {}
        for fmt in formats:
            mediaType = None  
            if fmt['mimeType'].startswith('audio/' + ext):
                mediaType = 'a'
            if fmt['mimeType'].startswith('video/' + ext):
                mediaType = 'v'
            if not mediaType:
                continue
            if mediaType == 'a':
                if not bool(maxAudio):
                    maxAudio = fmt
                else:
                    try:
                        if ('bitrate' in maxAudio) and ('bitrate' in fmt):
                            br_o = maxAudio['bitrate']
                            br_t = fmt['bitrate']
                            maxAudio = maxAudio if br_o > br_t else fmt
                    except Exception as err:
                        ColorHelper.print_red(err)  
            if mediaType == 'v':
                if not bool(maxVideo):
                    maxVideo = fmt
                else:
                    try:
                        pixel_o = maxVideo['width'] * maxVideo['height']
                        pixel_t = fmt['width'] * fmt['height']
                        if pixel_o < pixel_t:
                            maxVideo = fmt
                        elif pixel_o == pixel_t:
                            if ('bitrate' in maxVideo) and ('bitrate' in fmt):
                                br_o = maxVideo['bitrate']
                                br_t = fmt['bitrate']
                                maxVideo = maxVideo if br_o > br_t else fmt
                    except Exception as err:
                        ColorHelper.print_red(err) 
        return maxAudio, maxVideo

    def getV(self, url):
        query = urlsplit(url).query
        return parse_qs(query)['v'][0].strip()
        
    def isExist(self, v):
        try:
            with open(self.donefile, 'r') as file:
                return (v + '\n') in file.readlines()
        except Exception as err:
            ColorHelper.print_red(err)
        return False

    def markDownloaded(self, v):
        try:
            with open(self.donefile, 'a') as file:
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

    def isStop(self):
        if self.stopfile:
            if os.path.isfile(self.stopfile):
                return True
        return False
    
    def removeInvalidFilenameChars(self, filename):
        return filename.translate(str.maketrans('','',r'\/:*?"<>|'))

    def logfile(self, content, pr = True):
        if pr:
            print(content)
        with open(self.logsfile, 'a', encoding='utf-8') as f:
            f.write(str(content) + '\n')

    def fetchHandler(self, url, path, size, size_all, size_done, speed):
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
        # percent
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

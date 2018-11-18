#author: johnxguo
#date: 2018-11-7

import os, shutil
import sys
import asyncio
import json
from urllib.parse import urlsplit
from urllib.parse import parse_qs
from console_color.color_helper import ColorHelper
from youtubesession import YoutubeSession
from enum import Enum, unique
from speed import SpeedHelper
import xmltodict

class YoutubeDownloader:
    def __init__(self, session:YoutubeSession):
        self.session = session
        self.curTaskNum = 0
        self.maxTaskNum = 5
        self.fetchHandlerCounter = 0
        self.taskCounter = 0
        self.totalCount = 0
        self.doneCount = 0
        self.maxTaskCounter = sys.maxsize
        self.workpath = './'
        self.donefile = './youtube.donelist'
        self.errfile = './youtube.errlist'
        self.logsfile = './youtube.log'
        self.stopfile = './stop'
        self.prefix_v = 'https://www.youtube.com/watch?v='
        self.prefix_channel = 'https://www.youtube.com/channel/'
        self.prefix_playlist = 'https://www.youtube.com/playlist?list='
        self.continueurl = r'https://www.youtube.com/browse_ajax?ctoken=%s&continuation=%s&itct=%s'
        self.downloadinglist = []
        self.taskmap = {}
        self.speedHelper = SpeedHelper(100)
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

    def setErrfile(self, errfile):
        self.errfile = errfile
        return self

    def setLogsfile(self, logsfile):
        self.logsfile = logsfile
        return self
    
    def setStopfile(self, stopfile):
        self.stopfile = stopfile
        return self

    async def downloadPath(self, path):
        if path.startswith('#'):
            return True
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
                    ColorHelper.print_yellow('exist! v=%s'%(v), False, 1, ", " + v)
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
            contents = await self.processPlaylistInfo(0, info, contiHeaders)
            vids = [videoinfo['playlistVideoRenderer']['videoId'] for videoinfo in contents]
            ColorHelper.print_yellow(url + ' | total videos:' + str(len(vids)))
            tasks = [asyncio.ensure_future(self.downloadV(vid)) for vid in vids]
            await asyncio.wait(tasks)
        except Exception as err:
            ColorHelper.print_red(err)
            ColorHelper.print_red('get playlist fail, url=' + url)

    async def processPlaylistInfo(self, count, info, contiHeaders):
        contents = info['contents']
        playlistId = ''
        if 'playlistId' in info:
            playlistId = info['playlistId']
        try:
            contiinfo = info['continuations'][0]['nextContinuationData']
            continuation = contiinfo['continuation']
            itct = contiinfo['clickTrackingParams']
            contiurl = self.continueurl % (continuation, continuation, itct)
            rsp = await self.session.getWithHeaders(contiurl, contiHeaders) 
            json = self.getContiResponseJson(rsp)
            info_new = json['response']['continuationContents']['playlistVideoListContinuation']
            ColorHelper.print_green('analyzing playlist - %s, contents: %d' % (playlistId, (count + len(contents))))
            contents = contents + await self.processPlaylistInfo(count + len(contents), info_new, contiHeaders)
        except Exception:
            ColorHelper.print_blue('no more')
            pass
        return contents
        
    async def getRepresentations(self, dashmpd):
        if not dashmpd:
            return None
        try:
            xml_data = await self.session.get(dashmpd)
            j = xmltodict.parse(xml_data)
            adaptationSet = j['MPD']['Period']['AdaptationSet']
            formats = []
            for adaptation in adaptationSet:
                if not '@mimeType' in adaptation:
                    continue
                mimeType = adaptation['@mimeType']
                if 'Representation' in adaptation:
                    representation = adaptation['Representation']
                    for rep in  representation:
                        fmt = {'mimeType':mimeType}
                        if '@width' in rep:
                            fmt['width'] = int(rep['@width'])
                        if '@height' in rep:
                            fmt['height'] = int(rep['@height'])
                        if '@bandwidth' in rep:
                            fmt['bitrate'] = int(rep['@bandwidth'])
                        if 'BaseURL' in rep:
                            fmt['url'] = rep['BaseURL']
                        formats.append(fmt)
            return formats
        except Exception as err:
            ColorHelper.print_red(err)
            return None

    def getContiResponseJson(self, rsp):
        j = json.loads(rsp)
        for o in j:
            if 'response' in o:
                return o
        return None

    def getContiRequestHeaders(self, info):
        headers = {
            'X-YouTube-Variants-Checksum': str(info['VARIANTS_CHECKSUM']),
            'X-Youtube-Identity-Token': str(info['ID_TOKEN']),
            'X-YouTube-Page-CL': str(info['PAGE_CL']),
            'X-YouTube-Client-Name': '1',
            'X-YouTube-Client-Version': str(info['INNERTUBE_CONTEXT_CLIENT_VERSION']),
            'Accept-Encoding': 'gzip, deflate, br'
        }
        return headers

    def getConfigFromHtml1(self, html):
        st_str = r'ytplayer.config = '
        et_str = r"};"
        j = self.getConfigFromHtmlBase(html, st_str, et_str)
        return json.loads(j['args']['player_response']), j['args']['dashmpd'] if 'dashmpd' in j['args'] else None
    
    def getConfigFromHtml2(self, html):
        st_str = r'window["ytInitialData"] = '
        et_str = r"};"
        j = self.getConfigFromHtmlBase(html, st_str, et_str)
        return j['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']\
                ['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']

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
            ColorHelper.print_yellow('exist! v=%s'%(v), False, 1, ", " + v)
            return False
        if self.isStop():
            ColorHelper.print_red('global stop!', False, 2, "stop!")
            return False
        return True

    def increaseTotalCount(self):
        self.totalCount = self.totalCount + 1
        return self.totalCount

    def increaseDoneCount(self):
        self.doneCount = self.doneCount + 1
        return self.doneCount

    def increaseFetchHandlerCounter(self):
        self.fetchHandlerCounter = self.fetchHandlerCounter + 1
        return self.fetchHandlerCounter

    async def downloadV(self, v):
        if not self.checkDownloadState(v):
            return
        self.increaseTotalCount()
        while self.curTaskNum >= self.maxTaskNum:
            leftCount = int(self.totalCount - self.doneCount) % 100
            await asyncio.sleep(leftCount)
        # double check
        if not self.checkDownloadState(v):
            self.increaseDoneCount()
            return
        self.markDownloading(v)
        ColorHelper.print_cyan(r' ------ begin download v=%s ------ '%(v))
        self.curTaskNum = self.curTaskNum + 1
        try:
            url_v = self.prefix_v + v
            html_v = await self.session.get(url_v)
            player_response, dashmpd = self.getConfigFromHtml1(html_v)
            if not player_response:
                ColorHelper.print_red('get config fail, v=' + v)
                return False
            representations = await self.getRepresentations(dashmpd)
            videoDetails = player_response['videoDetails']
            formats = player_response['streamingData']['formats']
            if 'adaptiveFormats' in player_response['streamingData']:
                formats = formats + player_response['streamingData']['adaptiveFormats']
            if representations:
                formats = formats + representations
            title = videoDetails['title']
            pureTitle = self.removeInvalidFilenameChars(title)
            channel = videoDetails['channelId']
            filename = channel + ' - ' + pureTitle + ' - ' + v
            maxAudio, maxVideo = self.getMaxAV(formats)
            if not bool(maxVideo):
                self.onVErr(v)
                return False
            try:
                ext = '.webm'
                if maxVideo['mimeType'].startswith('video/mp4'):
                    ext = '.mp4'
                if not bool(maxAudio):
                    maxAudio = maxVideo
                tmpPath = self.workpath + 'tmp/'
                if not os.path.exists(tmpPath):
                    os.makedirs(tmpPath)
                videoPath = tmpPath + filename + '-video' + ext
                audioPath = tmpPath + filename + '-audio' + ext
                outptPath = self.workpath + filename + ext
                videoUrl = maxVideo['url']
                audioUrl = maxAudio['url']
                self.taskmap[videoUrl] = self.taskCounter
                self.taskCounter = self.taskCounter + 1
                self.taskmap[audioUrl] = self.taskCounter
                self.taskCounter = self.taskCounter + 1
                tasks = [
                    asyncio.ensure_future(self.session.fetch(videoUrl, videoPath, self.fetchHandler))
                ]
                if videoUrl != audioUrl:
                    tasks.append(asyncio.ensure_future(self.session.fetch(audioUrl, audioPath, self.fetchHandler)))
                await asyncio.wait(tasks)
                if self.isResultSucc(tasks):
                    ColorHelper.print_purple('merging audio and video..')
                    if videoUrl == audioUrl:
                        shutil.move(videoPath, outptPath)
                    else:
                        mergeCmd = 'ffmpeg -loglevel quiet -nostdin -y -i \"' + audioPath + '\" -i \"' + videoPath + '\" -acodec copy -vcodec copy \"' + outptPath + '\"'
                        os.system(mergeCmd)
                    self.markDownloaded(v)
                    ColorHelper.print_green(outptPath + ' is done, %4.1f%%  %d/%d'%((self.doneCount + 1)*100/self.totalCount, self.doneCount + 1, self.totalCount))
                    if os.path.exists(videoPath):
                        os.remove(videoPath)
                    if os.path.exists(audioPath):
                        os.remove(audioPath)
                else:
                    ColorHelper.print_red(r'network err! v=%s download fail!'%(v))
                self.taskmap.pop(videoUrl)
                if videoUrl != audioUrl:
                    self.taskmap.pop(audioUrl)
            except Exception as err:
                ColorHelper.print_red(err)
        except Exception as err:
            ColorHelper.print_red(err)
            self.onVErr(v)
            return False
        finally:
            self.increaseDoneCount()
            self.markNotDownloading(v)
            self.curTaskNum = self.curTaskNum - 1
        return True

    def onVErr(self, v):
        self.markErred(v)
        ColorHelper.print_red('get avconfig fail, v=%s, 视频已被删除'%(v))

    def isResultSucc(self, tasks):
        return len([task for task in tasks if not task.result()]) == 0

    def getMaxAV(self, formats):
        maxAudio_webm, maxVideo_webm = self.getMaxAVWithExt(formats, 'webm')
        maxAudio_mp4, maxVideo_mp4 = self.getMaxAVWithExt(formats, 'mp4')
        if not bool(maxVideo_webm):
            return maxAudio_mp4, maxVideo_mp4
        elif not bool(maxVideo_mp4):
            return maxAudio_webm, maxVideo_webm
        else:
            pixel_webm = maxVideo_webm['width'] * maxVideo_webm['height']
            pixel_mp4 = maxVideo_mp4['width'] * maxVideo_mp4['height']
            if pixel_webm < pixel_mp4:
                return maxAudio_mp4, maxVideo_mp4
            else:
                return maxAudio_webm, maxVideo_webm

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
            if not os.path.isfile(self.donefile):
                return False
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

    def isErred(self, v):
        try:
            if not os.path.isfile(self.errfile):
                return False
            with open(self.errfile, 'r') as file:
                return (v + '\n') in file.readlines()
        except Exception as err:
            ColorHelper.print_red(err)
        return False
    
    def markErred(self, v):
        try:
            with open(self.errfile, 'a') as file:
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
        return (not self.isExist(v)) and (not self.isErred(v)) and (not self.isDownloading(v))

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
        if self.increaseFetchHandlerCounter() % 100:
            return
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
        log = logname + ' | ' + "%4.1f%% "%(size_done*100/size_all) + '%8s' % self.sizeByte2Str(size_done) + \
              ' /' + '%8s' % self.sizeByte2Str(int(size_all)) + ' | ' + self.sizeByte2Str(speed) + '/s'
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

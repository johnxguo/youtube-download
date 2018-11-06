#author: johnxguo
#date: 2018-10-31

import os
import asyncio
import json
from console_color.color_helper import ColorHelper
from youtubedownloader import YoutubeDownloader
from youtubesession import YoutubeSession

# uvloop don't support windows
# import uvloop
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class YoutubeCmd:
    def __init__(self, configFile = None):
        self.configFile = configFile
        self.loadConfig()

    def start(self):
        param = (None, None)
        if not self.config:
            self.config = {}
        else:
            if self.config['username'] and self.config['password']:
                param = (self.config['username'], self.config['password'])
            elif self.config['login']:
                param = self.inputUserInfo()
        self.session = YoutubeSession(*param)
        if not self.session.username:
            ColorHelper.print_red('init failed! will exit.')
            exit()
        self.downloader = YoutubeDownloader(self.session)
        if self.config['maxTaskNum']:
            self.downloader.setMaxTaskNum(self.config['maxTaskNum'])
        if self.config['maxTaskCounter']:
            self.downloader.setMaxTaskCounter(self.config['maxTaskCounter'])
        if self.config['workpath']:
            self.downloader.setWorkPath(self.config['workpath'])
        ColorHelper.print_green("I'm ready!")
        if 'cmd' in self.config:
            print(self.session.username + ">" + self.config['cmd'])
            self.processCmd(self.config['cmd'])
        while 1:
            cmd = input(self.session.username + ">")
            if self.processCmd(cmd):
                break
        print("end")

    def processCmd(self, cmd):
        cmd = cmd.strip()
        if cmd == '' or cmd == None:
            return False
        if cmd == 'exit':
            return True
        elif cmd[:3] == 'dl ':
            path = cmd[3:]
            # uvloop
            self.asyncrun(self.downloader.downloadPath(path))
        else:
            if not self.asyncrun(self.downloader.downloadPath(cmd)):
                ColorHelper.print_red("no such command!")

    def inputUserInfo(self):
        return input('username:'), input('password:')

    def asyncrun(self, future):
        return asyncio.get_event_loop().run_until_complete(future)

    def loadConfig(self):
        try:
            if os.path.isfile(self.configFile):
                with open(self.configFile, 'r') as f:
                    config = json.loads(f.read())
                    if not 'username' in config:
                        config['username'] = None
                    if not 'password' in config:
                        config['password'] = None
                    if not 'maxTaskNum' in config:
                        config['maxTaskNum'] = None
                    if not 'maxTaskCounter' in config:
                        config['maxTaskCounter'] = None
                    if not 'workpath' in config:
                        config['workpath'] = './'
                    if not 'login' in config:
                        config['login'] = None
                    self.config = config
        except Exception as err:
            ColorHelper.print_red(r'load config[%s] fail, err:%s' % (self.configFile, str(err)))

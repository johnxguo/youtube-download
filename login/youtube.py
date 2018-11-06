#author: johnxguo
#date: 2018-10-31

from .google import GoogleLoginHelper
import os
import json

class YoutubeLoginHelper:
    def __init__(self, uid:str, password:str):
        self.googleLoginHelper = GoogleLoginHelper(uid, password)
        self.initPageUrl = 'https://www.youtube.com/account'

    def setUserInfo(self, uid:str, password:str):
        self.googleLoginHelper.setUserInfo(uid, password)

    def login(self):
        if self.isLoginOk():
            return self
        self.googleLoginHelper.login().turnTo(self.initPageUrl)
        if self.isLoginOk():
            print('login youtube succ!')
        else:
            print('login youtube fail!')
        return self
    
    def isLoginOk(self):
        return self.googleLoginHelper.isLoginOk()

    def getCookie(self):
        return self.googleLoginHelper.getCookie()

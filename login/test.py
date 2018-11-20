#author: johnxguo
#date: 2018-10-31

from .google import GoogleLoginHelper
from .youtube import YoutubeLoginHelper

class LoginTest:
    def __init__(self):
        self.cmds = {'1': (self.test_login_google, 'google'),
                     '2': (self.test_login_youtube, 'youtube'),
                     '3': (self.test_login_weibo, 'weibo'),
                     '4': (self.test_login_qq, 'qq'),
                     '5': (self.test_login_sis001, 'sis001')}

    def showLint(self):
        #print({k:v[1] for (k, v) in self.cmds.items()})
        print('\nLogin Test:')
        for k, v in self.cmds.items():
            print('  ' + k + ' - ' + v[1])
        print('  ? - help')

    def runTest(self):
        self.showLint()
        while 1:
            cmd = input("input>")
            cmd = cmd.strip()
            if cmd == '' or cmd == None:
                continue
            if (cmd == '?'):
                self.showLint()
                continue
            try:
                cmdInfo = self.cmds[cmd]
                if not cmdInfo:
                    continue
                cmdInfo[0](*self.inputUserInfo())
            except Exception:
                pass

    def inputUserInfo(self):
        return input('username:'), input('password:')

    def test_login_google(self, username, password):
        print(GoogleLoginHelper(username, password).login().getCookie()) 
        pass

    def test_login_youtube(self, username, password):
        print(YoutubeLoginHelper(username, password).login().getCookie()) 
        pass

    def test_login_weibo(self, username, password):
        pass

    def test_login_qq(self, username, password):
        pass

    def test_login_sis001(self, username, password):
        pass

LoginTest().runTest()
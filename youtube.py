#author: johnxguo
#date: 2018-11-7

import os

# requirements:
# 1. os.system('pip freeze > requirements.txt')
# 2. os.system('pip install -r requirements.txt')
# 3. download webdriver(ChromeDriver) from https://sites.google.com/a/chromium.org/chromedriver/downloads
# 4. copy the webdriver.exe to the path where the chrome.exe put 
# 5. config the above path to $PATH
# 6. config your proxy to config.proxy
# 7. config your download configs in config.json
# 8. install ffmpeg and add to the $PATH
# 9. pip3 install brotlipy

from youtubecmd import YoutubeCmd

YoutubeCmd('config.json').start()
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


# todo: 1.config里面设置最大下载的文件size，超过的忽略并log到日志文件，人工查验
#       2.通用缓存，playlist和logincache都接入
#       3.用size做缩略图的prefix，以此排序做人工查验，缩略图生成到子目录，人工查验完成之后自动删除对应的视频并重命名缩略图（此过程可重复执行）
#       4.从现有文件生成filelist，用donelist和filelist可以生成ignorelist，若donelist丢失，可以根据ignorelist重新下载。
#       5.用机器学习对缩略图做聚类，以便更好的做人工去重。
#       6.直接下载channel，媒体库，我关注的所有媒体库
#       7.方块符号进度条▉▉▉▉
#       8.密码显示星号
#       9.config.cmd 多个命令串行执行，分号分隔
#       10.断点续传
#       列出封面图片  决定是否下载

from downloader.youtubecmd import YoutubeCmd

YoutubeCmd('config.json').start()
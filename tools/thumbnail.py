import os
import sys

# 生成size做前缀的缩略图（到子目录），然后可以根据缩略图名删除（移动）原视频

class Thumbnail:
    def __init__(self, wordpath):
        self.workpath = wordpath
        self.thumbpath = wordpath + 'thumbnail/'
        self.ignorepath = wordpath + 'ignore/'
        if not os.path.isdir(self.thumbpath):
            os.makedirs(self.thumbpath)
        
    def genThumbnail(self):
        filelist = self.listfile(self.workpath)
        if not bool(filelist):
            print('Thumbnail: empty folder!')
            return
        cmdtmpl = r'ffmpeg -loglevel quiet -ss 00:00:10 -nostdin -y -i "%s" -filter:v scale="%s" -vframes 1 "%s"'
        counter = 0
        for filename in filelist:
            counter = counter + 1
            if not filename.endswith('.webm'):
                continue
            thumbname = filename[:-5] + '.png'
            thumbpath = self.thumbpath + thumbname
            if os.path.isfile(thumbpath):
                print('%4.1f%% %d/%d '%(counter * 100 /len(filelist), counter, len(filelist)) + ' continue')
                continue
            rso = self.getResolution(self.workpath + filename)
            l = 1600
            scale = f'{l}:-1' if rso['w'] > rso['h'] else f'-1:{l}'
            cmd = cmdtmpl % (self.workpath + filename, scale, thumbpath)
            os.system(cmd)
            print('%4.1f%% %d/%d '%(counter * 100 /len(filelist), counter, len(filelist)) + thumbname + ' done')

    def getResolution(self, path):
        cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "{path}"'
        try:        
            with os.popen(cmd) as f:
                res = f.read()
                rt = res.split('x')
                ret = {'w':1, 'h':1}
                ret = {'w':int(rt[0]), 'h':int(rt[1])}
        except Exception : 
            pass
        return ret
    
    def genThumbnailWithSize(self):
        
        pass

    def renameThumbnailWithSize(self):
        pass
    
    def renameThumbnailWithoutSize(self):
        pass
    
    def moveVideos(self):
        pass
 
    def listfile(self, path):
        filelist = []
        if os.path.isdir(path):
            filelist = os.listdir(path)
        return filelist


class ThumbnailCmd:
    def __init__(self, args):
        self.handleCmd(args)

    def handleCmd(self, args):
        opt = '-t'
        workpath = '.'
        if len(args) == 2:
            workpath = args[1]
            pass
        elif len(args) == 3:
            workpath = args[1]
            opt = args[2]
            pass
        else:
            print('参数错误')
            return
        thumb = Thumbnail(workpath)
        self.methods = {
            '-t': thumb.genThumbnail,
            '-s': thumb.renameThumbnailWithSize,
            '-ts': thumb.genThumbnailWithSize,
            '-st': thumb.genThumbnailWithSize,
            '-ns': thumb.renameThumbnailWithoutSize,
            '-m': thumb.moveVideos
        }
        if opt in self.methods:
            (self.methods[opt])()
        else:
            print('参数错误')
            return


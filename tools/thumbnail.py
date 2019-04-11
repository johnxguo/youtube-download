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
        cmdtmpl = r'ffmpeg -loglevel quiet -ss 00:00:10 -nostdin -y -i "%s" -filter:v scale="1024:-1" -vframes 1 "%s"'
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
            cmd = cmdtmpl % (self.workpath, thumbpath)
            os.system(cmd)
            print('%4.1f%% %d/%d '%(counter * 100 /len(filelist), counter, len(filelist)) + thumbname + ' done')
    
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
        if len(sys.argv) == 2:
            workpath = sys.argv[0]
            pass
        elif len(sys.argv) == 3:
            opt = sys.argv[0]
            workpath = sys.argv[1]
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






    
Thumbnail(sys.argv)
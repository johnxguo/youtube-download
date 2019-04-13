import os
import sys
from console.console import Console

def GenTmpVlst(tmppath, vlst):
    if not os.path.isdir(tmppath):
        Console.print_red('目录不存在：%s' % (tmppath)) 
        return
    files = os.listdir(tmppath)
    baseUrl = 'https://www.youtube.com/watch?v=%s'
    urls = {*()}

    for filename in files:
        v = filename[filename.rfind(' - ') + 3 : filename.rfind('-')]
        urls.add(baseUrl % (v))

    with open(vlst, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')
            Console.print_yellow(url)

    Console.print_green('\ntotal: %d\nvlst : %s' % (len(urls), vlst))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        Console.print_red('参数错误')
        exit()
    GenTmpVlst(sys.argv[1], sys.argv[2])



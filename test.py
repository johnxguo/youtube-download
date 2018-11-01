#author: johnxguo
#date: 2018-10-28

import os
import aiohttp
import asyncio
from youtube import YoutubeSession

async def logfile(content, filename):
    rsp = await session.fetch(content, filename)
#    with open(filename, 'w', encoding='utf-8') as f:
#        print (rsp, file = f)

session = YoutubeSession()
tasks = [
    asyncio.ensure_future(logfile(r'https://r2---sn-npoe7ne6.googlevideo.com/videoplayback?keepalive=yes&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313&requiressl=yes&gir=yes&lmt=1537445700965008&expire=1541043586&initcwndbps=515000&mn=sn-npoe7ne6%2Csn-i3belne6&c=web&ipbits=0&mm=31%2C26&id=0fab42d69cabb133&mv=m&dur=5029.941&mt=1541021899&ms=au%2Conr&ip=195.123.237.227&clen=10912821081&fvip=2&signature=CB3A77CEF10B85B9856CB450A5CA904025EC5928.679D72FEF88CCD1FA574900DE45B5F64DD32581D&itag=313&ei=IiHaW-7tKIOzogOo67OQBw&sparams=aitags%2Cclen%2Cdur%2Cei%2Cgir%2Cid%2Cinitcwndbps%2Cip%2Cipbits%2Citag%2Ckeepalive%2Clmt%2Cmime%2Cmm%2Cmn%2Cms%2Cmv%2Cpl%2Crequiressl%2Csource%2Cexpire&key=yt6&source=youtube&pl=25&mime=video%2Fwebm&alr=yes&cpn=MaUoS9tqJBs1eMkM&cver=html5', '1.html')),
    asyncio.ensure_future(logfile(r'https://r4---sn-npoe7ne7.googlevideo.com/videoplayback?key=yt6&clen=2964946198&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398&txp=5532432&sparams=aitags%2Cclen%2Cdur%2Cei%2Cgir%2Cid%2Cinitcwndbps%2Cip%2Cipbits%2Citag%2Ckeepalive%2Clmt%2Cmime%2Cmm%2Cmn%2Cms%2Cmv%2Cpl%2Crequiressl%2Csource%2Cexpire&mt=1541022978&gir=yes&requiressl=yes&ip=195.123.237.227&keepalive=yes&mv=m&source=youtube&ms=au%2Conr&signature=344622A0A4DAEF5E1EA470FC9ACE10F3E48C24B0.9007861644EA2D1A68850212C3F1F3FA06AD8097&mime=video%2Fwebm&dur=1776.307&fvip=4&pl=25&initcwndbps=371250&id=05ecb85d7240a92f&itag=313&mn=sn-npoe7ne7%2Csn-i3beln76&mm=31%2C26&ipbits=0&expire=1541044657&c=web&ei=USXaW7zPHIuwz7sPoJWBmAo&lmt=1540313690389751&alr=yes&cpn=5-X6fClQc9CCNEwj&cver=html5&', '2.html')),
]
async def main():
    return await asyncio.gather(*tasks)

asyncio.get_event_loop().run_until_complete(main())



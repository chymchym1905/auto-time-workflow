#pip install yt_dlp
#pip install https://github.com/seproDev/yt-dlp-ChromeCookieUnlock/archive/main.zip
import yt_dlp
import sys
import os
import json
def main(videos):
    print(videos)
    ydl_opts = {'paths':{'home':os.path.join(os.getcwd(),"downloads/")},
                'format':'bv',
                'outtmpl':'%(title)s.%(ext)s',
                'overwrite':True,
                # 'listformats':True,
                # 'cookiesfrombrowser':('edge',),
                # 'cookiefile':cookies,
                'verbose':True,}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # print(json.dumps(ydl.extract_info('https://www.youtube.com/watch?v=Zdk6sVYZABE', download=False),indent=4))
        ydl.download(videos)

if __name__ == '__main__':
    main(sys.argv[1:])
    
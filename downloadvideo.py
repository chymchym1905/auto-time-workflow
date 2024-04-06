#pip install yt_dlp
#pip install https://github.com/seproDev/yt-dlp-ChromeCookieUnlock/archive/main.zip
import yt_dlp
import sys
import os
import json
def main(videos):
    ydl_opts = {'paths':{'home':os.path.join(os.getcwd(),"downloads/")},
                'format':'bv',
                'outtmpl':'%(title)s.%(ext)s',
                'overwrite':True,
                # 'listformats':True,
                # 'cookiesfrombrowser':('edge',),
                # 'cookiefile':cookies,
                'verbose':True,}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # print(json.dumps(ydl.extract_info('"https://www.youtube.com/watch?v=9yj3coh_jJA&t=440s"', download=False),indent=4))
        for i in videos:
            try:
                ydl.download([i])  
            except: print(f"{i} IS UNAVAILABLE")

if __name__ == '__main__':
    main(sys.argv[1:])
    
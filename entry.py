#pip install yt_dlp
#pip install https://github.com/seproDev/yt-dlp-ChromeCookieUnlock/archive/main.zip
import yt_dlp
import sys
import os
import pickle
from checkgpu import checkgpu
from infer import inference
from timeruns import timeruns

def split_list(a_list):
    half = len(a_list) // 2
    return a_list[:half], a_list[half:]

def main(args):
    ydl_opts = {'paths':{'home':os.path.join(os.getcwd(),"downloads/")},
                'format':'bv',
                'outtmpl':'%(title)s.%(ext)s',
                'overwrite':True,
                # 'listformats':True,
                # 'cookiesfrombrowser':('edge',),
                # 'cookiefile':cookies,
                }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        videos, num_chambers = split_list(args)
        downloadedvideos = []
        for i, video in enumerate(videos):
            try:
                ydl.download([video])
                downloadedvideos += [video]
            except:
                num_chambers.pop(i)
                print(f"{video} IS UNAVAILABLE")
        print(f"Downloaded videos: {downloadedvideos}")
        print(f"Num chambers: {num_chambers}")
        gpu = checkgpu()
        infres = inference(gpu)
        # infres = []
        # for file in os.listdir("framedata"):
        #     with open(os.path.join("framedata",file), 'rb') as f:
        #         infres.append(pickle.load(f))
        try:
            timeruns(num_chambers, infres)
        except ValueError as e:
            print(e)

if __name__ == '__main__':
    main(sys.argv[1:])
    
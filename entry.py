# pip install yt_dlp
# pip install https://github.com/seproDev/yt-dlp-ChromeCookieUnlock/archive/main.zip
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
    ydl_opts = {
        "paths": {"home": os.path.join(os.getcwd(), "downloads/")},
        "format": "bv",
        "outtmpl": "%(title)s.%(ext)s",
        "overwrite": True,
        "format_sort": ["res:1080"],
        # 'listformats':True,
        # 'cookiesfrombrowser':('edge',),
        # 'cookiefile':cookies,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        videos, num_chambers = split_list(args)
        downloadedvideos, num = [], []
        for i, video in enumerate(videos):
            try:
                ydl.download([video])
                downloadedvideos += [video]
                num += [num_chambers[i]]
            except:
                print(f"{video} IS UNAVAILABLE")
        print(f"Downloaded videos: {downloadedvideos}")
        print(f"Num chambers: {num}")
        gpu = checkgpu()
        infres = inference(gpu)
        # infres = []
        # for file in os.listdir("framedata"):
        #     with open(os.path.join("framedata",file), 'rb') as f:
        #         infres.append(pickle.load(f))
        timeruns(num, infres)


if __name__ == "__main__":
    main(sys.argv[1:])

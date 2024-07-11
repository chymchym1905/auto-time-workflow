# pip install yt_dlp
# pip install https://github.com/seproDev/yt-dlp-ChromeCookieUnlock/archive/main.zip
import yt_dlp
import sys
import os
import pickle
import json
import requests
from checkgpu import checkgpu
from infer import getpath, infer, inference
from timeruns import timeruns, timerunsv2

one_room = ["12-1-1", "12-1-2", "12-2-1", "12-2-2", "12-3-1", "12-3-2"]
two_rooms = ["12-1", "12-2", "12-3"]
three_rooms = ["12-top", "12-bot"]
six_rooms = ["12-all"]


def split_list(a_list):
    half = len(a_list) // 2
    return a_list[:half], a_list[half:]


def login(email, password):
    url = "https://tgh-server-v2.herokuapp.com/api/authentication"
    response = requests.post(
        url,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        data=json.dumps({"userEmail": email, "password": password}),
    )
    if response.status_code == 200:
        json_data = response.json()
        authHeaders = json_data["authToken"]
        return authHeaders
    else:
        return "Error"


def main(args):
    final_filename = "filename"
    ### Unapproved abyss runs
    url = "https://tgh-server-v2.herokuapp.com/api/speedrun-entries/agent-all?page=0&approved=false&sortBy=created_at&sortDir=asc"
    ### 5 most recent approved abyss runs
    # url = "https://tgh-server-v2.herokuapp.com/api/speedrun-entries/agent-all?limit=5&page=0&approved=true&sortBy=created_at&sortDir=desc"
    authHeaders = login("daugiakien@gmail.com", "Kakashi0\\")
    response: requests.Response = requests.get(
        url,
        headers={"Authorization": authHeaders},
    )
    runs = response.json()["entries"]["rows"]
    if runs == []:
        print("No runs to verify")
        sys.exit(1)
    print(runs)
    videos, num_chambers = [], []
    for i in runs:
        if i["speedrun_category"] != "Abyss":
            continue
        videos += [i["video_link"]]
        if i["speedrun_subcategory"] in one_room:
            num_chambers += [1]
        elif i["speedrun_subcategory"] in two_rooms:
            num_chambers += [2]
        elif i["speedrun_subcategory"] in three_rooms:
            num_chambers += [3]
        elif i["speedrun_subcategory"] in six_rooms:
            num_chambers += [6]

    def yt_dlp_monitor(self):
        nonlocal final_filename
        final_filename = self.get("filename")

    ydl_opts = {
        "paths": {"home": os.path.join(os.getcwd(), "downloads/")},
        "format": "bv",
        "outtmpl": "%(id)s.%(ext)s",
        "overwrite": True,
        "format_sort": ["res:1080"],
        # "verbose": True,
        "progress_hooks": [yt_dlp_monitor],
        # "proxy": "34.92.250.88:10000",
        # 'listformats':True,
        # 'cookiesfrombrowser':('edge',),
        # 'cookiefile':cookies,
    }
    infer_res = []
    results = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        downloadedvideos, num = [], []
        for i, video in enumerate(videos):
            try:
                ydl.download([video])
                downloadedvideos += [video]
                num += [num_chambers[i]]
                gpu = checkgpu()
                print(final_filename)
                alreadytimed = False
                for video in os.listdir("results"):
                    if video[:-4] in final_filename:
                        print("Video already timed")
                        alreadytimed = True
                        with open(f"results/{video}", "r") as f:
                            results += [int(float(f.read()))]
                        break
                if alreadytimed:
                    continue
                timeresult = infer(final_filename, gpu)
                if timeresult == None:
                    print("file path not found")
                    continue
                infer_res.append(timeresult)
                # infres = inference(gpu)
                # results = timeruns(num, infer_res)
                results += [
                    timerunsv2(num_chambers[i], getpath(final_filename), timeresult)
                ]
            except Exception as e:
                print(e)
                print(f"{video} cannot be timed. Skipping...")
        print(f"Downloaded videos: {downloadedvideos}")
        print(f"Num chambers: {num}")
        if len(downloadedvideos) == 0:
            print("No videos downloaded. Exiting...")
            sys.exit(1)
        validruns = []
        for entry in runs:
            if entry["video_link"] not in downloadedvideos:
                continue
            validruns += [entry]
        print(f"Valid runs: {validruns}; Results: {results}")
        for run, time in zip(validruns, results):
            print(f'Updating run {run["video_link"]} with time {time}')
            run["time"] = time
            run["notes"] = (
                "Video auto time by chym's bot. Please contact chymchym1905 on discord if result is off by a few frames or completely incorrect"
            )
            updateurl = (
                "https://tgh-server-v2.herokuapp.com/api/speedrun-entries/update"
            )
            requests.post(updateurl, headers={"Authorization": authHeaders}, json=run)
        print(validruns)


if __name__ == "__main__":

    main(sys.argv[1:])

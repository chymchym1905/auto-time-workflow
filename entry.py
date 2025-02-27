# pip install yt_dlp
# pip install https://github.com/seproDev/yt-dlp-ChromeCookieUnlock/archive/main.zip
from typing import List
import yt_dlp
import sys
import os
import pickle
import json
import requests
import traceback
from checkgpu import checkgpu
from infer import getpath, infer, inference
from plot import plot
from timeruns import savetime, timeruns, timerunsv2
from yt_dlp.utils import download_range_func

one_room = ["12-1-1", "12-1-2", "12-2-1", "12-2-2", "12-3-1", "12-3-2"]
two_rooms = ["12-1", "12-2", "12-3"]
three_rooms = ["12-top", "12-bot"]
six_rooms = ["12-all"]
email = ""
password = ""
MAINURL = "https://genshin.tghofficial.com/api"
TESTURL = "http://localhost:3001/api"
with open("auth/password.txt", "r") as f:
    password = f.read()


def split_list(a_list):
    half = len(a_list) // 2
    return a_list[:half], a_list[half:]


def login(url, userEmail, userPassword):
    response = requests.post(
        url,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        data=json.dumps({"userEmail": userEmail, "password": userPassword}),
    )
    if response.status_code == 200:
        json_data = response.json()
        authHeaders = json_data["authToken"]
        return authHeaders
    else:
        return "Error"


def main(args):
    apiurl = MAINURL
    global email
    with open("auth/email.txt", "r") as f:
        email = f.read()
    if len(args) > 0 and args[0] == "test":
        apiurl = TESTURL
        with open("auth/testmail.txt", "r") as f:
            email = f.read()
    ### Unapproved abyss runs
    url = f"{apiurl}/speedrun-entries/agent-all?limit=1000&speedrun_category=Abyss&page=0&approved=false&sortBy=created_at&sortDir=asc"
    ### 5 most recent approved abyss runs
    # url = f"{apiurl}/speedrun-entries/agent-all?limit=5&page=0&approved=true&sortBy=created_at&sortDir=desc"
    ### time runs from a competitor
    # url = f"{apiurl}/speedrun-entries/all?competitor=66f8280dec087c8e78b07062&sortBy=created_at&sortDir=asc&limit=10&page=0"
    authHeaders = login(f"{apiurl}/authentication", email, password)
    response: requests.Response = requests.get(
        url,
        headers={"Authorization": authHeaders},
    )
    rawAPIentries = response.json()["entries"]["rows"]
    if rawAPIentries == []:
        print("No runs to verify")
        sys.exit(1)
    print(rawAPIentries)
    videos, num_chambers, vidsegment = [], [], []
    for i in rawAPIentries:
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
        if "video_segment" in i:
            vidsegment += [i["video_segment"]]
        else:
            vidsegment += [["NA-NA"]]

    timedResults = []
    for i, video in enumerate(videos):
        res = timeonevideo(video, num_chambers[i], vidsegment[i])
        timedResults += [res] if res is not None else []

    for i in timedResults:
        print(f"Video url: {i['url']}")
        print(f"Num chambers: {i['num_chambers']}")
        print(f"Video segment: {i['vid_segment']}")
        print(f"Time: {i['time']}")
    if len(timedResults) == 0:
        print("No videos downloaded. Exiting...")
        sys.exit(1)
    validEntries = []
    for entry in rawAPIentries:
        if entry["video_link"] not in list(map(lambda x: x["url"], timedResults)):
            continue
        validEntries += [entry]
    for run, resdict in zip(validEntries, timedResults):
        print(f'Updating run {run["video_link"]} with time {resdict["time"]}')
        run["time"] = resdict["time"]
        run["notes"] = (
            "Video auto time by chym's bot. You can either accept this time or manually time it if it's off by too much."
        )
        updateurl = f"{apiurl}/speedrun-entries/update"
        requests.post(updateurl, headers={"Authorization": authHeaders}, json=run)
    print(validEntries)


def timeonevideo(videourl, numchamber, vidsegment: list[str]):
    video_result = {
        "url": videourl,
        "num_chambers": numchamber,
        "vid_segment": vidsegment,
        "objects_present": [],
        "time": 0,
    }
    try:
        ydl_opts = {
            "paths": {"home": os.path.join(os.getcwd(), "downloads/")},
            "format": "bv",
            "outtmpl": "%(id)s.%(ext)s",
            "overwrite": True,
            "format_sort": ["res:1080"],
            # "verbose": True,
            # "proxy": "34.92.250.88:10000",
            # 'listformats':True,
            # 'cookiesfrombrowser':('edge',),
            # 'cookiefile':cookies,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([videourl])
            video_id = ydl.extract_info(videourl).get("id", "")
            gpu = checkgpu()
            filename = getvideofilename(video_id)
            time = 0
            currsegmenttext = " ".join(vidsegment)
            alreadytimed, video_result["time"] = checkVideoStatus(
                video_id, currsegmenttext
            )
            if alreadytimed:
                return video_result
            if vidsegment == []:
                vidsegment = ["NA-NA"]  # for the case where there is no segment
            for index, segmentvalue in enumerate(vidsegment):
                alreadytimed, segmenttime = checkVideoStatus(video_id, segmentvalue)
                if alreadytimed:
                    time += segmenttime
                    continue
                timeresult = infer(f"downloads/{filename}", gpu, vidsegment[index])
                video_result["objects_present"] += timeresult
                segmenttime = timerunsv2(
                    numchamber / len(vidsegment),
                    filename,
                    createfilenamewithsegment(filename, segmentvalue),
                    timeresult,
                    save=True if len(vidsegment) > 1 else False,
                )
                time += segmenttime
            video_result["time"] = time
            plot(video_result["objects_present"], f"{video_id}${currsegmenttext}$")
            savetime(f"{video_id}${currsegmenttext}$", time)
    except Exception as e:
        print("Exception occurred:")
        print(e)
        print("Call stack:")
        traceback.print_exc()
        print(f"{videourl} cannot be timed. Skipping...")
        return None
    return video_result


def checkVideoStatus(vidid, segmenttext):
    alreadytimed = False
    time = 0
    for video in os.listdir("results"):
        segment = ""
        try:
            segment = video.split("$")[1]
        except:
            segment = ""
        if vidid in video and (
            segment == segmenttext or (segmenttext == "NA-NA" and segment == "")
        ):
            alreadytimed = True
            with open(f"results/{video}", "r") as f:
                time = int(float(f.read()))
                print("Video already timed: ", time)
            break
    return (alreadytimed, time)


def createfilenamewithsegment(filename: str, segment: str) -> str:
    ### filename = videoid.ext
    ### segment format videoid$start-end$.ext
    return f"{filename.split('.')[0]}${segment}$.{filename.split('.')[1]}"


def getvideofilename(video_id) -> str:
    return next((video for video in os.listdir("downloads") if video_id in video), None)


if __name__ == "__main__":

    main(sys.argv[1:])

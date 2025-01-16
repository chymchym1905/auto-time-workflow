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
MAINURL = "https://tgh-server-v2.herokuapp.com/api"
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
    runs = response.json()["entries"]["rows"]
    if runs == []:
        print("No runs to verify")
        sys.exit(1)
    print(runs)
    videos, num_chambers, vidsegment = [], [], []
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
        if "video_segment" in i:
            vidsegment += [i["video_segment"]]
        else:
            vidsegment += [[]]

    results = []
    for i, video in enumerate(videos):
        res = timeonevideo(video, num_chambers[i], vidsegment[i])
        results += [res] if res is not None else []

    for i in results:
        print(f"Video url: {i['url']}")
        print(f"Num chambers: {i['num_chambers']}")
        print(f"Video segment: {i['vid_segment']}")
        print(f"Time: {i['time']}")
    if len(results) == 0:
        print("No videos downloaded. Exiting...")
        sys.exit(1)
    validruns = []
    for entry in runs:
        if entry["video_link"] not in list(map(lambda x: x["url"], results)):
            continue
        validruns += [entry]
    for run, resdict in zip(validruns, results):
        print(f'Updating run {run["video_link"]} with time {resdict["time"]}')
        run["time"] = resdict["time"]
        run["notes"] = (
            "Video auto time by chym's bot. You can either accept this time or manually time it if it's off by too much."
        )
        updateurl = f"{apiurl}/speedrun-entries/update"
        requests.post(updateurl, headers={"Authorization": authHeaders}, json=run)
    print(validruns)


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
            # filestotime = getvideosegmentsfromfilename(video_id, vidsegment)
            filename = getvideofilename(video_id)
            time = 0
            alreadytimed = False
            currsegmenttext = getsegmenttext(vidsegment)
            for video in os.listdir("results"):
                filenametocheck = f"{video_id}${currsegmenttext}$.txt"
                if video == filenametocheck:
                    print("Video already timed")
                    alreadytimed = True
                    with open(f"results/{video}", "r") as f:
                        video_result["time"] = int(float(f.read()))
                    break
            if alreadytimed:
                return video_result
            # Process the segments
            # processed_segments = process_segments(vidsegment)
            if vidsegment == []:
                vidsegment = ["NA-NA"]  # for the case where there is no segment
            for index, segmentvalue in enumerate(vidsegment):
                timeresult = infer(f"downloads/{filename}", gpu, vidsegment[index])
                video_result["objects_present"] += timeresult
                segmenttime = timerunsv2(
                    numchamber / len(vidsegment),
                    filename,
                    createfilenamewithsegment(filename, segmentvalue),
                    timeresult,
                    save=True,
                )
                time += segmenttime
            video_result["time"] = time
            plot(video_result["objects_present"], f"{video_id}${currsegmenttext}$")
            savetime(f"{video_id}${currsegmenttext}$", time)

            # timeresult = infer(final_filename, gpu)  # return objects_present
            # if timeresult == None:
            #     print("file path not found")
            #     return None
            # video_result["objects_present"] = timeresult
            # video_result["time"] = timerunsv2(
            #     numchamber, getpath(final_filename), timeresult
            # )  # return time
    except Exception as e:
        print("Exception occurred:")
        print(e)
        print("Call stack:")
        traceback.print_exc()
        print(f"{videourl} cannot be timed. Skipping...")
        return None
    return video_result


# Return video file name that match the segments
def getvideosegmentsfromfilename(video_id, segment: list[str]) -> list[str]:
    res = []
    for video in os.listdir("downloads"):
        segmenttext = video.split("$")[1].split(".")[0]
        if segment == []:
            if video_id in video and segmenttext == "NA-NA":
                return [video]
        else:
            if video_id in video and segmenttext in segment:
                res += [video]
    return res


def createfilenamewithsegment(filename, segment):
    file = filename.split(".")
    return f"{file[0]}${segment}$.{file[1]}"


def getvideofilename(video_id):
    for video in os.listdir("downloads"):
        if video_id in video:
            return video
    return None


def getsegmenttext(segment: list[str]) -> str:
    if segment == []:
        return "NA-NA"
    return " ".join(segment)


if __name__ == "__main__":

    main(sys.argv[1:])

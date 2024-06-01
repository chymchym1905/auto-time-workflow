# pip install yt_dlp
# pip install https://github.com/seproDev/yt-dlp-ChromeCookieUnlock/archive/main.zip
import sys
import os
import requests
from checkgpu import checkgpu
from infer import inference
from timeruns import timeruns
import json
import boto3

accesskey = os.environ.get("AWS_ACCESS_KEY_ID")
secretkey = os.environ.get("AWS_SECRET_ACCESS_KEY")

boto3.setup_default_session(region_name="us-west-2")
client = boto3.client(
    "lambda",
    aws_access_key_id=accesskey,
    aws_secret_access_key=secretkey,
)


def split_list(a_list):
    half = len(a_list) // 2
    return a_list[:half], a_list[half:]


def main(args):
    videos, num_chambers = split_list(args)
    response = client.invoke(
        FunctionName="getVideo",
        InvocationType="RequestResponse",
        Payload=json.dumps({"videos": videos}),
    )
    payload = json.loads(response["Payload"].read())
    payload = payload[::-1]
    downloadedvideos, num = [], []
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    # print(json.dumps(payload, indent=4))
    for i, vid in enumerate(payload):
        if vid["error"] != "None":
            print(f"{vid['error']}")
            continue
        print(f"Downloading {vid['title']}")
        response = requests.get(vid["video"])
        filepath = f"downloads/{vid['title']}.mp4"
        with open(filepath, "wb") as video_file:
            try:
                for chunk in response.iter_content():
                    video_file.write(chunk)
                downloadedvideos += [f"{vid['title']}.mp4"]
                num += [num_chambers[i]]
            except Exception as e:
                print(f"ERROR: {e}")
    print(f"Downloaded videos: {downloadedvideos}")
    print(f"Num chambers: {num}")
    if len(downloadedvideos) == 0:
        print("No videos downloaded. Exiting...")
        sys.exit(1)
    gpu = checkgpu()
    infres = inference(gpu)
    # infres = []
    # for file in os.listdir("framedata"):
    #     with open(os.path.join("framedata",file), 'rb') as f:
    #         infres.append(pickle.load(f))
    timeruns(num, infres)


if __name__ == "__main__":
    main(sys.argv[1:])

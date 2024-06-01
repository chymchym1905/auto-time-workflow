# pip install yt_dlp
# pip install https://github.com/seproDev/yt-dlp-ChromeCookieUnlock/archive/main.zip
import sys
import os
import requests
from checkgpu import *
from infer import inference
from timeruns import timeruns
import json
import mimetypes
from urllib.parse import urlparse, parse_qs


def get_extension_from_url(url):
    # Parse the URL and extract query parameters
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Get the MIME type from the query parameters
    mime_type = query_params.get("mime", [None])[0]

    if not mime_type:
        raise ValueError("MIME type not found in URL")

    # Get the file extension based on the MIME type
    extension = mimetypes.guess_extension(mime_type)

    if not extension:
        raise ValueError("Could not determine file extension from MIME type")

    return extension


def split_list(a_list):
    half = len(a_list) // 2
    return a_list[:half], a_list[half:]


def main(args):
    videos, num_chambers = split_list(args)
    response = client.invoke(
        FunctionName="getVideo",
        InvocationType="RequestResponse",
        Payload=json.dumps({"videos": videos, "inferring": True}),
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
        filepath = rf"downloads/{vid['id']}{get_extension_from_url(vid['video'])}"
        with open(filepath, "wb") as video_file:
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    video_file.write(chunk)
                downloadedvideos += [filepath]
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

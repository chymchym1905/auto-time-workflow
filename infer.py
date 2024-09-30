import cv2
from ultralytics import YOLO
from ultralytics.engine.results import Results
import numpy as np
import os
import torch
import pickle
from tqdm import tqdm
import plot
import math
import re


def checkdirtyframeutil(presentframe):
    nonabyssframes = ["overworld", "character-screen"]
    for i in nonabyssframes:
        if i in presentframe:
            return True


# dirty frame is ignored and don't get scanned by object detect
def check_dirty_frame(res_classify: Results):
    # name: dictionary of classes
    # probs: probabilities of each class
    name, prob = list(res_classify.names.values()), res_classify.probs.data.tolist()
    presentframe = []
    for i in range(len(prob)):
        if prob[i] > 0.1:  # add class if prob > 0.1
            presentframe.append(name[i])
    if len(presentframe) > 2:  # 3 or more classes
        return True
    elif (
        "abyss" not in presentframe and len(presentframe) > 1
    ):  # abyss not present and 2 or more classes
        return True
    elif (
        "abyss" in presentframe
        and len(presentframe) > 1
        and checkdirtyframeutil(presentframe)
    ):
        # abyss present and at least one of them is outside abyss
        return True
    else:
        return False


def getpath(video):
    return video.split("downloads/")[1]


def infer(vidpath, gpu):
    # Combine classify and object detect
    # Time video
    detect_model = YOLO(r"deploymodel/detect.pt").to(
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    classify_model = YOLO(r"deploymodel/classify.pt").to(
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    video_title = getpath(vidpath)
    print(video_title)
    if video_title == None:
        return
    # do not touch
    if not os.path.exists("videos"):
        os.makedirs("videos")
    outputpath = rf"videos/{video_title}annotated.mp4"
    cap = cv2.VideoCapture(vidpath)
    # Get video details
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(math.ceil(cap.get(cv2.CAP_PROP_FPS)))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    objects_present = []
    # Define codec and create VideoWriter object to save annotated video
    codec = "avc1" if gpu == True else "XVID"
    fourcc = cv2.VideoWriter_fourcc(*codec)  # Codec for the output video
    # temppath = r'videos/temp.mp4' if gpu==True else r'videos/temp.avi'
    out = cv2.VideoWriter(outputpath, fourcc, fps, (frame_width, frame_height))
    count = 1
    for _ in tqdm(
        range(total_frames), total=total_frames, desc=f"Processing {video_title}"
    ):
        ret, img = cap.read()
        if ret == False:
            break
        count += 1
        # img = image_resize(img, width=640)
        resultclassify: Results = classify_model.predict(source=img, verbose=False)
        resultclassify = resultclassify[0]
        height, width, _ = img.shape
        offset = height
        if check_dirty_frame(resultclassify) == False:
            objects_present += [
                list(
                    resultclassify.names[index]
                    for index, i in enumerate(resultclassify.probs.data.tolist())
                    if i > 0.1
                )
            ]
            for name, prob in zip(
                resultclassify.names.values(), resultclassify.probs.data.tolist()
            ):
                if prob > 0.1:  # prob of any class
                    offset -= int(height / 12)
                    cv2.putText(
                        img,
                        name + " " + str("{:.2f}".format(prob * 100)) + "%",
                        (int(width / 12), offset),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        2,
                        (6, 6, 254),
                        5,
                    )
                if name == "abyss" and prob > 0.1:  # prob of abyss
                    resultdetect: Results = detect_model.predict(
                        source=img, verbose=False
                    )
                    resultdetect = resultdetect[0]
                    boxes = resultdetect.boxes
                    objects_present[-1] += [
                        detect_model.names[int(box.cls)]
                        for box in boxes
                        if round(box.conf.item() * 100, 2) > 75
                    ]
                    for box in boxes:
                        (x, y, x1, y1) = np.array(
                            box.xyxy.cpu(), dtype=int
                        ).squeeze()  # get box coordinates in (left, top, right, bottom) format
                        class_index = box.cls
                        cv2.rectangle(img, (x, y), (x1, y1), (36, 255, 12), 2)
                        cv2.putText(
                            img,
                            detect_model.names[int(class_index)]
                            + " "
                            + str(round(box.conf.item() * 100, 2))
                            + "%",
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (36, 255, 12),
                            2,
                        )
        else:
            objects_present += [["Dirty Frame"]]
            for name, prob in zip(
                resultclassify.names.values(), resultclassify.probs.data.tolist()
            ):
                if prob > 0.1:  # prob of any class
                    offset -= int(height / 12)
                    cv2.putText(
                        img,
                        name + " " + str("{:.2f}".format(prob * 100)) + "%",
                        (int(width / 12), offset),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        2,
                        (6, 6, 254),
                        5,
                    )
            offset -= int(height / 12)
            cv2.putText(
                img,
                "Dirty Frame",
                (int(width / 12), offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (6, 6, 254),
                5,
            )
        out.write(img)
    cap.release()
    out.release()
    # if os.path.exists(outputpath):
    #     os.remove(outputpath)
    # os.rename(temppath, outputpath)
    if not os.path.exists("framedata"):
        os.makedirs("framedata")
    with open(f"framedata/{video_title}.pkl", "wb") as f:
        pickle.dump(objects_present, f)
    # plot.plot(objects_present, video_title)
    return objects_present


def inference(gpu):
    infres = []
    for videos in os.listdir("downloads"):
        infres.append(infer(os.path.join("downloads", videos), gpu))
    return infres

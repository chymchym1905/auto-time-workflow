from enum import Enum
from collections import Counter 
import cv2
import os
from functools import reduce

class Platform(Enum):
    PC = 'skill-icons'
    MOBILE = 'skill-icons-mobile'
    CONTROLLER = 'skill-icons-controller'

class Chamber():
    def __init__(self, start_frame=0, end_frame=0, platform = None, paused=False, fps=60):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.platform = platform
        self.paused = paused
        self.fps = fps

    def __str__(self):
        return f"Frame info: {self.start_frame}-{self.end_frame} \nPlatform: {self.platform} \nPaused: {self.paused} \nFPS: {self.fps} \nTime: {self.time()}"
    
    def getChamberInfo(self):
        return {'start_frame': self.start_frame, 
                'end_frame': self.end_frame, 
                'platform': self.platform, 
                'paused': self.paused, 
                'fps': self.fps}
    
    def time(self):
        if self.end_frame == 0 or self.start_frame == 0 or self.end_frame<self.start_frame:
            return "Not enough data to calculate time"
        return (self.end_frame - self.start_frame)/self.fps
    
    def getTime(self):
        if self.end_frame == 0: return "End frame must be greater than 0"
        if self.start_frame == 0: return "Start frame must be greater than 0"
        if self.end_frame<self.start_frame: return "End frame must be greater than start frame"

        return (self.end_frame - self.start_frame)/self.fps


def flatten(lst):
    return [item for sublist in lst for item in sublist]

def find_start_end(objects, icon):
    for i, x in enumerate(objects):
        if icon in x:
            start = i
            break
    for i, x in enumerate(objects[::-1]):
        if 'objective-text' in x:
            end = i
            break
    end = len(objects) - end -1
    return start, end

def transform_tuples(tuples, start, end):
    new_tuples = [(start, tuples[0][0])]
    new_tuples += [(tuples[i][1], tuples[i+1][0]) for i in range(len(tuples)-1)]
    new_tuples.append((tuples[-1][1], end))
    return new_tuples

def find_gaps(objects: list, start, end, numchambers):
    
    # Initialize variables
    zero_indices = [start] + [i for i, x in enumerate(objects) if 'objective-text' in x] + [end]
    gaps = [(zero_indices[i-1], zero_indices[i]) for i in range(1, len(zero_indices))]

    # Calculate gap lengths
    gap_lengths = [end - start - 1 for start, end in gaps]

    # Find the indices of the two largest gaps
    largest_gap_indices = sorted(range(len(gap_lengths)), key=lambda i: gap_lengths[i], reverse=True)[:numchambers]
    gaps = [gaps[i] for i in largest_gap_indices]

    return sorted(gaps, key=lambda x: x[0])

def find_platform(objects):
    lst = flatten(objects)
    c = Counter(lst)
    maxcount = 0
    platform = Platform.PC
    for ele, count in c.most_common():
        if ele in ['skill-icons', 'skill-icons-controller', 'skill-icons-mobile']:
            if count > maxcount:
                maxcount = count
                platform = ele
    return platform


def find_skill_icons(objects: list, icon, gaps, start, end):
    skill_icons = [start]
    for (chamberbegin, chamberend) in gaps:
        endchamberindex = 0
        for i in list(range(chamberbegin,chamberend))[::-1]:
            if 'transition-screen' in objects[i] or 'transition-screen-2' in objects[i]:
                endchamberindex = i
                # print(i)
                break
    
        for i in list(range(endchamberindex, chamberend)):
            if icon in objects[i]:
                skill_icons.append(i)
                break
    return skill_icons
            
def verify_run(object_list, fps, numchambers, title):
    icon = find_platform(object_list)
    start, end = find_start_end(object_list, icon)
    gaps = find_gaps(object_list, start, end, numchambers-1)
    print(title)
    print(gaps)
    starts = find_skill_icons(object_list, icon, gaps, start, end)
    print('Starting frames: ', starts)
    ends =  [x for (x,y) in gaps] + [end]
    print('Ending frames: ',ends)
    if len(starts) != len(ends): raise ValueError('Bad video error')
    chambers: list[Chamber] = []
    for x,y in zip(starts,ends):
        chambers += [Chamber(start_frame=x, end_frame=y, platform=icon, fps=fps)]
    totalTime = 0
    for i, chamber in enumerate(chambers):
        print(f'Chamber {i+1}: {chamber.getTime()}')
        totalTime += chamber.getTime()
    print('Total time: ',totalTime, '\n')
    return chambers, totalTime

def get_fps(video_path):
    video_capture = cv2.VideoCapture(video_path)
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    video_capture.release()
    
    return fps

def savetime(filename, content):
    if not os.path.exists("results"):
        os.makedirs("results")
    with open(f"results/{filename}.txt", "w") as file:
        file.write(str(content))

def timeruns(num_chambers:  list[int], infres):
    for video, framedata, numchamber in zip(os.listdir("downloads"), infres, num_chambers):
        try:
            objects_present = framedata
            res = verify_run(objects_present,int(get_fps(os.path.join("downloads",video))), int(numchamber), video)
            savetime(video, res[1])
        except Exception as e:
            savetime(video, e)
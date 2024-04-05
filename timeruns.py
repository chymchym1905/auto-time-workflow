from enum import Enum
from collections import Counter 
import cv2
import os
import pickle
from functools import reduce
import sys

class Platform(Enum):
    PC = 'skill-icons'
    MOBILE = 'skill-icons-mobile'
    CONTROLLER = 'skill-icons-controller'

class Chamber():
    def __init__(self, fps):
        self.start_frame = 0
        self.end_frame=0
        self.platform = None
        self.paused = False
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
        assert self.end_frame>0, "End frame must be greater than 0"
        assert self.start_frame>0, "Start frame must be greater than 0"
        assert self.end_frame>self.start_frame, "End frame must be greater than start frame"

        return (self.end_frame - self.start_frame)/self.fps


def flatten(lst):
    return [item for sublist in lst for item in sublist]

def frame_look_ahead(objectlist ,lookaheadquota):
    #this function look ahead in object list and
    #return None if there's objective-text in the follow up frames (lookaheadquota) is usually 2s
    #the sample is taken from the start of objectlist to lookaheadquota
    """return the objects present in the sample and occurence frequency if there's an end screen in the follow up frames"""
    pauses = ['BP-screen', 'coop-screen', 'book-screen', 'mission-screen', 'tutorial-screen', 'wish-screen',
              'map-screen', 'Dirty Frame']
    endscreens = ['transition-screen', 'transition-screen-2','character-screen','overworld','abyss', 'Dirty Frame']
    # abyssobjectives = ['abyss','objective-text','skill-icons','skill-icons-controller','skill-icons-mobile']
    if lookaheadquota>len(objectlist):
        lookaheadquota = len(objectlist)
    lst = objectlist[:lookaheadquota]
    lst = flatten(lst)
    counter = Counter(lst,)
    res = counter.most_common()
    object = [i[0] for i in res]
    occurence = [i[1] for i in res]
    print(object, occurence)
    if 'objective-text' in object:
        if occurence[object.index('objective-text')] >= 10:
            return None
        # if bool(set(object) & set(pauses)):
        #     return set(object) & set(pauses)
    if check_end_screen1(object, occurence) == True:
        return object, occurence
    
    

def getPlatform(objectlist: list):
    for frame in objectlist:
        if 'skill-icons' in frame:     
            return Platform.PC
        if 'skill-icons-controller' in frame:
            return Platform.CONTROLLER
        if 'skill-icons-mobile' in frame:
            return Platform.MOBILE

def check_end_screen1(objects:list, occurence):
    #check for if endscreens are in the passed objects list
    #return True if the number of occurences of a single endcreen is bigger than 10
    endscreens = ['transition-screen', 'transition-screen-2','character-screen', 'overworld']
    for i in endscreens:
        if i in objects:
            if occurence[objects.index(i)] >= 10:
                return True
    return False

def find_element_index(nested_list, element, skipindexes):
    #find the first element in the nestedlist that match "{element}"
    #if there's an objective-text in the frame, it will skip the frame, otherwise it will return the index
    #of the element that match "{element}"
    """return the index of the element or None"""
    for outer_index, inner_list in enumerate(nested_list):
        if outer_index < skipindexes:
            continue
        if element in inner_list and 'objective-text' not in inner_list:
            return outer_index

def verify_start_frame(objectlist: list, start_frame: int, skillicon, fps):
    #verify the start frame of the chamber picked by find_element_index()
    """return boolean"""
    transitionframes = ['transition-screen', 'transition-screen-2']
    sample = objectlist[start_frame: start_frame + fps * 2]
    sample = flatten(sample)
    counter = Counter(sample)
    res = counter.most_common()
    object = [i[0] for i in res]
    occurence = [i[1] for i in res]
    if 'objective-text' not in object and set(object).intersection(transitionframes) != set():
        return False
    else: return True


def verify_chamber(objectlist: list, framerate, skippedframes=0):
    #objectlist: list of objects present in video
    #framerate: fps of video
    #skippedframes: number of frames to skip while scanning
    """return a chamber object and the ending frame of the chamber"""
    endscreens = ['transition-screen', 'transition-screen-2','character-screen','overworld', 'Dirty Frame']
    abyss_pauses = ['BP-screen', 'coop-screen', 'book-screen', 'mission-screen', 'tutorial-screen', 'wish-screen',
              'map-screen', 'Dirty Frame']
    lookaheadquota = framerate*2
    chamber = Chamber(fps=framerate)
    chamber.platform = getPlatform(objectlist)

    chamber.start_frame = find_element_index(objectlist, chamber.platform.value, skippedframes)
    skipframes = chamber.start_frame
    if skipframes == None:
        raise ValueError('Video ended or verification in previous chamber failed. Please check video.')
    while verify_start_frame(objectlist, skipframes, chamber.platform, framerate) == False:
        chamber.start_frame = find_element_index(objectlist, chamber.platform.value, skipframes)
        skipframes += framerate
        print(skipframes)
    print('Start frame:',chamber.start_frame, 'Skipped to frame:', skippedframes)
    chamber_ending = 0

    for i, frame in enumerate(objectlist):
        # iterate through the object list
        if i < skippedframes: continue #skip previous timed chambers
        if 'objective-text' in frame:
            if set(frame).intersection(endscreens) == set(): continue
            # if objective text is present and not an end screen
        elif 'objective-text' not in frame:
            res = frame_look_ahead(objectlist[i:], lookaheadquota)
            print(i, res,'\n')
            if res is None: continue
            lookaheadobjects, lookaheadoccurences = res
            if not set(lookaheadobjects).issubset(endscreens) and set(lookaheadobjects).intersection(endscreens) == set():
                continue
            if set(lookaheadobjects).issubset(abyss_pauses): chamber.paused = True
            elif check_end_screen1(lookaheadobjects, lookaheadoccurences) == True and 'objective-text' in objectlist[i-1]: 
                chamber.end_frame = i-1
                chamber_ending = i
                print("end frame found")
                break
    return chamber, chamber_ending

def verify_run(objectlist: list, framerate, no_rooms):
    #return a list of chamber
    chambers = []
    video_mark=0
    for i in range(no_rooms):
        print('Chamber: ',i,'Starting point:', video_mark)
        chamber, video_mark = verify_chamber(objectlist, framerate, skippedframes=video_mark+1 if video_mark>0 else video_mark)
        chambers += [chamber]
        print(chamber,'\n')
    return chambers

def get_fps(video_path):
    video_capture = cv2.VideoCapture(video_path)
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    video_capture.release()
    
    return fps

class TimedResults():
    def __init__(self, timedresult:list[Chamber]):
        self.timedresult = reduce(lambda x,y: x.getTime() + y.getTime(), timedresult) if len(timedresult)>1 else timedresult[0].getTime()
    
    def savetime(self, filename):
        if not os.path.exists("results"):
            os.makedirs("results")
        with open(f"results/{filename}.txt", "w") as file:
            file.write(str(self.timedresult))

if __name__ == '__main__':
    num_chambers = sys.argv[1:]
    for video, framedata in zip(os.listdir("downloads"), os.listdir("framedata")):
        with open(os.path.join("framedata",framedata), "rb") as file:
            objects_present = pickle.load(file)
        res = [TimedResults(verify_run(objects_present,int(get_fps(os.path.join("downloads",video))), int(x))) for x in num_chambers]
        for i in res:
            i.savetime(video)
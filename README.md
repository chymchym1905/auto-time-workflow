# ML pipeline use to auto time speedruns
YOLOv8 model, Paperspace workflows
## Handmade dataset
[Object detection dataset](https://universe.roboflow.com/auto-time/autotime)

[Classification dataset](https://universe.roboflow.com/auto-time/auto-time-classify)

In order to run this script, you need might need to install OpenH624 for opencv. Put open264 dll inside 
`AppData\Local\Programs\Python\Python310\Lib\site-packages\cv2` or the location that contains opencv

Install Python at least 3.8 and install the required package. Virutal environment is optional
Windows venv:
```
py -m venv .venv
.venv\Scripts\activate.bat
```
Mac or Linux (py for windows and python or python3 for Mac/Linux):
```
python -m venv .venv
source .venv/bin/activate
```
Install required packages:
```cmd
pip install -U -r requirements.txt
```
Go to [Pytorch website](https://pytorch.org/get-started/locally/) and install torch with the corresponding CUDA version. If you are not training using gpu, just install pytorch normally, if you are training it's required to install CUDA Toolkit and cuDNN and follow instructions at pytorch website to install the according pytorch package

No training:
```
pip install pytorch
```


Go to https://github.com/cisco/openh264/releases, download the openh264 dll and put into cv2 package folder IF you need standard mp4 format. Installing Openh264 is required to export inferred video in AVC1 codec (mp4 format), or else OpenCV won't export the video. You can just use XVID (avi or mkv format) and not bother with openh264, as long as you don't bother with video codec problem.

Go to https://ffmpeg.org/, download and add ffmpeg binary to environment variables. FFMPEG is not needed with new verion of the script

Run this to fetch all unverified Abyss speedruns and start timing:
```
py entry.py
```

You need an Agent account or an Admin account on TGH to perform this action

# ML pipeline use to auto time speedruns
YOLOv8 model, Paperspace workflows
## Handmade dataset
[Object detection dataset](https://universe.roboflow.com/auto-time/autotime)

[Classification dataset](https://universe.roboflow.com/auto-time/auto-time-classify)

In order to run this script, you need might need to install OpenH624 for opencv. Put open264 dll inside 
`AppData\Local\Programs\Python\Python310\Lib\site-packages\cv2` or the location that contains opencv

Run:
```cmd
pip install -U -r requirements.txt

Go to https://pytorch.org/get-started/locally/ and install torch with the corresponding CUDA version

Go to https://github.com/cisco/openh264/releases, download the openh264 dll and put into cv2 package folder

Go to https://ffmpeg.org/, download and add ffmpeg binary to environment variables

py entry.py
```

You need an Agent account or an Admin account on TGH to perform this action

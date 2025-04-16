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

// Don't need to install CUDA toolkit if you are just inferencing
Go to https://pytorch.org/get-started/locally/ and install torch with the corresponding CUDA version
pip install pytorch (if not training using gpu, if you are training it's required
to install CUDA Toolkit and cuDNN)

Go to https://github.com/cisco/openh264/releases, download the openh264 dll and put into cv2 package folder
openh264 codec is needed to encode output video in mp4, if you don't want to
you could use XVID in infer.py

Go to https://ffmpeg.org/, download and add ffmpeg binary to environment variables
FFMPEG is not needed with new verion of the script

py entry.py
```

You need an Agent account or an Admin account on TGH to perform this action

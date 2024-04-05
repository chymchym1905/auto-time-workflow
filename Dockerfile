FROM ultralytics/ultralytics:latest-cpu

# Install any needed packages specified in requirements.txt
RUN pip install pytube yt-dlp easyocr
RUN pip uninstall opencv-python opencv-python-headless -y
RUN pip install opencv-python-headless
ENV PYTHONUNBUFFERED=TRUE

CMD ["ls"]

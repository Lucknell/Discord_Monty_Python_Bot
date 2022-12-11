FROM ubuntu:latest
MAINTAINER lucknell <lucknell3@gmail.com>
ENV TZ "America/Los_Angeles"
RUN mkdir -p /src/bot/
RUN apt update && apt upgrade -y && DEBIAN_FRONTEND=noninteractive apt install -y python3 python3-pip python-pil ffmpeg espeak-ng libespeak1 tesseract-ocr libjpeg-dev zlib1g-dev libffi-dev firefox git gnupg wget
WORKDIR /src/bot
RUN git clone https://github.com/Rapptz/discord.py
RUN cd discord.py && python3 -m pip install -U .[voice]
RUN pip3 install -U quart Quart-Discord discord.py-ipc Pillow pyttsx3 PyNaCl requests pytesseract numpy beautifulsoup4 geckodriver-autoinstaller selenium emoji PyMongo

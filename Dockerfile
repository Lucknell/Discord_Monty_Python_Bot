FROM jgoerzen/debian-base-security
MAINTAINER lucknell <lucknell3@gmail.com>                                              
RUN mkdir -p /src/bot/
RUN apt update && apt upgrade -y && apt install -y python3 python3-pip ffmpeg espeak-ng libespeak1 tesseract-ocr firefox-esr
WORKDIR /src/bot                                                                
COPY . /src/bot   
RUN pip3 install -U discord.py pyttsx3 PyNaCl requests pytesseract numpy beautifulsoup4 geckodriver-autoinstaller selenium
CMD ["python3", "-u", "monty.py"]
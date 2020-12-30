FROM jgoerzen/debian-base-security
MAINTAINER lucknell <lucknell3@gmail.com>                                              
RUN mkdir -p /src/bot/
RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg espeak python-espeak libespeak1 tesseract-ocr
WORKDIR /src/bot                                                                
COPY . /src/bot   
RUN pip3 install -U discord.py pyttsx3 PyNaCl requests pytesseract numpy
LABEL com.centurylinklabs.watchtower.enable="false"
CMD ["python3", "-X", "faulthandler", "-u", "monty.py"]
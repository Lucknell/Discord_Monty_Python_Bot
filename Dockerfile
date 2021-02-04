FROM ubuntu:latest
MAINTAINER lucknell <lucknell3@gmail.com>                                              
RUN mkdir -p /src/bot/
RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg espeak python-espeak libespeak1 tesseract-ocr firefox firefox-geckodriver
WORKDIR /src/bot                                                                
COPY . /src/bot   
RUN pip3 install -U discord.py pyttsx3 PyNaCl requests pytesseract numpy beautifulsoup4
CMD ["python3", "-u", "monty.py"]
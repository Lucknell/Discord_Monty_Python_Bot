FROM archlinux:latest
MAINTAINER lucknell <lucknell3@gmail.com>
ENV TZ "America/Los_Angeles"
RUN pacman -Syu --noconfirm && pacman -S --noconfirm base-devel firefox python python-pip ffmpeg tesseract tesseract-data-eng libjpeg-turbo zlib libffi git gnupg wget curl espeak-ng gcc
RUN mkdir -p /src/bot/ && mkdir -p /home/monty
RUN useradd -m -G wheel -s /bin/bash monty
RUN sed -Ei 's/^#\ (%wheel.*NOPASSWD.*)/\1/' /etc/sudoers
RUN chown monty:monty /src/bot/ && chown monty:monty /home/monty
COPY --chown=monty:monty requirements.txt /src/bot/.
USER monty
WORKDIR /src/bot
RUN git clone https://github.com/Rapptz/discord.py && cd discord.py && python3 -m pip install  --break-system-packages -U .[voice]
RUN pip3 install  --break-system-packages -r requirements.txt
RUN python3 -m spacy download en_core_web_sm --break-system-packages
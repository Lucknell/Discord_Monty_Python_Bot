FROM archlinux:latest
MAINTAINER lucknell <lucknell3@gmail.com>
ENV TZ "America/Los_Angeles"
RUN pacman-key --init 
RUN pacman-key --populate archlinux
RUN pacman-key --refresh-key && pacman -Syu --noconfirm
RUN pacman -Sy --noconfirm base-devel firefox python python-pip ffmpeg tesseract tesseract-data-eng libjpeg-turbo zlib libffi git gnupg wget curl espeak-ng gcc
RUN mkdir -p /src/bot/ && mkdir -p /home/monty
RUN useradd -m -G wheel -s /bin/bash monty
RUN sed -Ei 's/^#\ (%wheel.*NOPASSWD.*)/\1/' /etc/sudoers
RUN chown monty:monty /src/bot/ && chown monty:monty /home/monty
COPY --chown=monty:monty base/requirements.txt /src/bot/.
RUN mkdir /venv && chown monty:monty /venv
USER monty
WORKDIR /src/bot
RUN python3 -m venv /venv
ENV PATH=/venv/bin:$PATH
RUN git clone https://github.com/Rapptz/discord.py && cd discord.py && /venv/bin/python3 -m pip install  -U .[voice]
RUN /venv/bin/python3 -m pip install -r requirements.txt
RUN /venv/bin/python3 -m spacy download en_core_web_sm

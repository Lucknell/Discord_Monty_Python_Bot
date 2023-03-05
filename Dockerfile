FROM monty_python:latest
MAINTAINER lucknell <lucknell3@gmail.com>
COPY . /src/bot
CMD ["./run.sh"]

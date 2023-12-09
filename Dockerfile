FROM monty_python:latest
MAINTAINER lucknell <lucknell3@gmail.com>
COPY --chown=monty:monty . /src/bot
CMD ["./run.sh"]

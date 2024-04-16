FROM monty_python:latest
MAINTAINER lucknell <lucknell3@gmail.com>
COPY --chown=monty:monty cogs /src/bot/cogs/
COPY --chown=monty:monty meme /src/bot/meme/
COPY --chown=monty:monty templates /src/bot/templates/
COPY --chown=monty:monty static /src/bot/static/
COPY --chown=monty:monty monty.py /src/bot/.
COPY --chown=monty:monty server.py /src/bot/.
COPY --chown=monty:monty run.sh /src/bot/.
COPY --chown=monty:monty avatar.png /src/bot/.
CMD ["./run.sh"]

FROM monty_base:v1
MAINTAINER lucknell <lucknell3@gmail.com>                                              
COPY . /src/bot   
CMD ["python3", "-u", "monty.py"]
FROM monty_base:v1
MAINTAINER lucknell <lucknell3@gmail.com>                                              
COPY . /src/bot   
CMD ["./run.sh"]

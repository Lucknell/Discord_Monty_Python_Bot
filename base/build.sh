#docker images
#docker tag <image id> monty_base
cd ../
docker build -f base/Dockerfile -t monty_python:latest .
cd -
#!/bin/bash

export QUART_APP=server:app
#git config --global credential.helper store
#huggingface-cli login --token $HF_TOKEN --add-to-git-credential
cd /src/bot/server
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. Instagram.proto
mkdir grpc -p
mv Instagram.proto grpc/
cd grpc
protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative   Instagram.proto
go mod init grpc/grpc_instagram_server
cd /src/bot/server
go mod init main
go mod edit -replace grpc/grpc_instagram_server=./grpc
go mod tidy 
exec python3 -u grpc_server.py &
exec go run . &
cd /src/bot/
exec python3 -u -m quart  run --host=0.0.0.0 -p 5101 &
exec python3 -u /src/bot/monty.py

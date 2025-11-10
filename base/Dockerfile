FROM debian:trixie-slim
ENV TZ="America/Los_Angeles"
RUN apt update
RUN apt upgrade -y
RUN apt install -y python3 python3-pip python3-venv ffmpeg espeak-ng libespeak1 tesseract-ocr firefox-esr libjpeg62-turbo zlib1g libffi-dev git gnupg wget curl espeak-ng gcc libc-devtools golang-go vim cmake protobuf-compiler
RUN mkdir -p /src/bot/
RUN adduser --disabled-password --gecos " " --home "/home/monty" monty
RUN chown monty:monty /src/bot/
COPY --chown=monty:monty base/requirements.txt /src/bot/.
RUN mkdir /venv && chown monty:monty /venv
USER monty
WORKDIR /src/bot
RUN python3 -m venv /venv
ENV PATH=/venv/bin:$PATH
RUN git clone https://github.com/Rapptz/discord.py && cd discord.py && python3 -m pip install -U .[voice]
RUN go clean -modcache
RUN go mod init Server
RUN go get -u github.com/lrstanley/go-ytdlp@latest
RUN go get github.com/gorilla/mux
RUN go get go.mongodb.org/mongo-driver/v2/bson
RUN go get go.mongodb.org/mongo-driver/v2/mongo
RUN go get go.mongodb.org/mongo-driver/v2/mongo/options
RUN go get go.mongodb.org/mongo-driver/v2/mongo
RUN go get github.com/sklyt/whisper
RUN go get github.com/sklyt/whisper/pkg
RUN go get github.com/ollama/ollama/api
RUN go get github.com/u2takey/ffmpeg-go
RUN go mod download github.com/google/uuid
RUN go get github.com/gorilla/websocket
RUN go get github.com/tmc/langchaingo/llms/ollama
RUN go get github.com/ggerganov/whisper.cpp/bindings/go/pkg/whisper
RUN go get github.com/go-audio/audio
RUN go get github.com/go-audio/wav
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
RUN go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
RUN git clone https://github.com/ggml-org/whisper.cpp.git
ENV CGO_CFLAGS="-I/src/bot/whisper.cpp/include -I/src/bot/whisper.cpp/ggml/include"
ENV CGO_LDFLAGS="-L/src/bot/whisper.cpp/build_go/ggml/src -L/src/bot/whisper.cpp/build_go/src"
RUN cd whisper.cpp/bindings/go && make whisper
RUN python3 -m pip install --upgrade setuptools pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt

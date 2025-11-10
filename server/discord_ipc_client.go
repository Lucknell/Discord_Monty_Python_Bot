package main

import (
	"encoding/json"
	"fmt"
	"log"
	"log/slog"
	"net/http"

	"github.com/gorilla/websocket"
)

type DiscordClient struct {
	host           string
	standard_port  uint16
	secret_key     string
	multicast_port uint16
	do_multicast   bool
	timeout        uint16
	id             string
	//websocketclientprotocol
}

type Message struct {
	decoding      string
	code          uint8
	response      string
	error_type    string
	error_details string
	payload       string
	Secret        string `json:"secret"`
	length        uint16
	Endpoint      string `json:"endpoint"`
	data          string
	Kwargs        map[string]string `json:"kwargs"`
	Id            string            `json:"ID"`
}

func clientMaker() DiscordClient {
	var client DiscordClient

	client.host = "127.0.0.1"
	client.standard_port = 1025
	client.multicast_port = 20000
	client.do_multicast = true
	client.timeout = 0

	return client
}

func (dc DiscordClient) Post_Ipc(endpoint string) {

	wsURL := fmt.Sprintf("ws://%s:%d/", dc.host, dc.standard_port)
	message := Message{
		Endpoint: endpoint,
		Secret:   dc.secret_key,
		Kwargs:   nil,
	}
	header := make(http.Header)
	header.Set("ID", dc.id)
	c, _, err := websocket.DefaultDialer.Dial(wsURL, header)
	if err != nil {
		log.Fatal("dial:", err)
	}

	jsonData, err := json.Marshal(message)
	slog.Info(string(jsonData))
	slog.Info(string([]byte(jsonData)))
	if err != nil {
		log.Fatal(err)
	}

	err = c.WriteMessage(websocket.TextMessage, []byte(jsonData))
	if err != nil {
		log.Println("write:", err)
		return
	}
	go func() {
		for {
			_, message, err := c.ReadMessage()
			if err != nil {
				log.Println("read:", err)
				return
			}
			log.Printf("recv: %s", message)
		}
	}()
	//defer c.Close()

}

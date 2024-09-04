package common

import (
	"bufio"
	"io"
	"net"
	//"fmt"
)

type Protocol struct {
	socketServer net.Conn
}

func NewProtocol(socketServer net.Conn) *Protocol {
	protocol := &Protocol{
		socketServer: socketServer,
	}
	return protocol
}

func (p *Protocol) SendAll(msg string) error {
	totalBytes := len(msg)
	sentBytes := 0

	for sentBytes < totalBytes {
		n, err := p.socketServer.Write([]byte(msg[sentBytes:]))
		if err != nil {
			return err
		}
		sentBytes += n
	}
	return nil

}

func (p *Protocol) ReceiveAll(ID string) (string, error){
	var msg string
	reader := bufio.NewReader(p.socketServer)

	for {
		part, err := reader.ReadString('\n')
		msg += part

		if err == io.EOF {
			break
		}

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v", ID, err)
			return "", err
		}

		if len(part) > 0 && part[len(part)-1] == '\n' {
			break
		}
	}

	log.Infof("action: receive_message | result: success | client_id: %v | msg: %v", ID, msg)
	return msg, nil


}
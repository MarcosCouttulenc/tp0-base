package common

import (
	"bufio"
	"net"
	"fmt"
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

func (p *Protocol) SendAll(ID string, msgID int) {
	fmt.Fprintf(
		p.socketServer,
		"[CLIENT %v] Message N°%v\n",
		ID,
		msgID,
	)
}

func (p *Protocol) ReceiveAll(ID string) {
	msg, err := bufio.NewReader(p.socketServer).ReadString('\n')
	p.socketServer.Close()

	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			ID,
			err,
		)
		return
	}

	log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
		ID,
		msg,
	)
}
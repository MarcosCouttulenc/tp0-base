package common

import (
	"net"
	"time"
	"os"
	"encoding/csv"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
	BatchMaxAmount int
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	reader *csv.Reader
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, reader *csv.Reader) *Client {
	client := &Client{
		config: config,
		reader: reader,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

func (c *Client) CreateMessage(agencia string) *Message {
	nombre := os.Getenv("NOMBRE")
	apellido := os.Getenv("APELLIDO")
	documento := os.Getenv("DOCUMENTO")
	nacimiento := os.Getenv("NACIMIENTO")
	numero := os.Getenv("NUMERO")

	return NewMessage(agencia, nombre, apellido, documento, nacimiento, numero)
}


func (c *Client) ReadCsvRecord() ([]string, error) {
	record, err := c.reader.Read()
	if err != nil {
		return nil, err
	}
	return record, nil
}

func (c *Client) CreateMessageWithCsvRecord(record []string, agencia string) *Message {
	nombre := record[0]
	apellido := record[1]
	documento := record[2]
	nacimiento := record[3]
	numero := record[4]

	return NewMessage(agencia, nombre, apellido, documento, nacimiento, numero)
}


// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	endFile := false

	for !endFile{
		c.createClientSocket()
		protocol := NewProtocol(c.conn)
		batch := ""
		betsSent := 0
		// Create the connection the server in every loop iteration. Send an
		for actualBet := 1; actualBet <= c.config.BatchMaxAmount; actualBet++ {
			csvRecord, err := c.ReadCsvRecord()
			if err != nil {
				if err.Error() == "EOF" {
					// Final del archivo alcanzado
					endFile = true
					break
				}
	
				log.Fatalf("Error al leer el registro: %v", err)
			}

		message := c.CreateMessageWithCsvRecord(csvRecord, c.config.ID)
		messageToSend := message.Serialize()
		batch += messageToSend
		betsSent += 1


		}
		



		// message := c.CreateMessage(c.config.ID)

		batch += "\n"

		sizeInBytes := len(batch)
		sizeInKB := float64(sizeInBytes) / 1024
		

		err := protocol.SendAll(batch)
		result := "success"
		if err != nil {
			result = err.Error()
			log.Errorf("action: apuestas_enviadas | result: %v | cantidad_enviadas: %v | tam msj: %v KB", result, betsSent, sizeInKB)
		} else {
			log.Infof("action: apuestas_enviadas | result: %v | cantidad_enviadas: %v | tam msj: %v KB", result, betsSent, sizeInKB)
		}
		


		protocol.ReceiveAll(c.config.ID)

		// Wait a time between sending one message and the next one

		batch = ""
		time.Sleep(c.config.LoopPeriod)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}

// cierra la conexion con el server
func (c *Client) Cleanup() {
	if c.conn != nil {
		log.Infof("CERRANDO CONEXION CON EL SERVER, CLIENTE CON ID: %v", c.config.ID)
		c.conn.Close()
	}
}
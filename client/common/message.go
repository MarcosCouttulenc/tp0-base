package common

import (
	"fmt"
)

type Message struct {
	agencia string
	nombre string
	apellido string
	documento string
	nacimiento string
	numero string
}

func NewMessage(agencia string, nombre string, apellido string, documento string, nacimiento string, numero string) *Message {
	message := &Message{
		agencia: agencia,
		nombre: nombre,
		apellido: apellido,
		documento: documento,
		nacimiento: nacimiento,
		numero: numero,
	}
	return message
}

func (m *Message) Serialize() string {
	return fmt.Sprintf(
		"%s\n%s\n%s\n%s\n%s\n%s\n\n",
		m.agencia,
		m.nombre,
		m.apellido,
		m.documento,
		m.nacimiento,
		m.numero,
	)
}
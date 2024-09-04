package common

import (
	"fmt"
)

type Message struct {
	nombre string
	apellido string
	documento string
	nacimiento string
	numero string
}

func NewMessage(nombre string, apellido string, documento string, nacimiento string, numero string) *Message {
	message := &Message{
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
		"%s\n%s\n%s\n%s\n%s",
		m.nombre,
		m.apellido,
		m.documento,
		m.nacimiento,
		m.numero,
	)
}
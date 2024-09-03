#make docker-compose-up


NOMBRE_CONTAINER_SERVER="server"

PUERTO="12345"

MENSAJE_DE_PRUEBA="Hello World!"

MENSAJE_RECIBIDO=$(docker run --rm --network tp0_testing_net busybox sh -c "echo \"$MENSAJE_DE_PRUEBA\" | nc \"$NOMBRE_CONTAINER_SERVER\" \"$PUERTO\"")

if [ "$MENSAJE_RECIBIDO" == "$MENSAJE_DE_PRUEBA" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi

#make docker-compose-down
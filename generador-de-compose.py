import sys

def generar_compose(archivo_salida, cantidad_de_clientes):
    texto_a_escribir = "name: tp0\n"
    texto_a_escribir += "services:\n"
    texto_a_escribir += "  server:\n"
    texto_a_escribir += "    container_name: server\n"
    texto_a_escribir += "    image: server:latest\n"
    texto_a_escribir += "    entrypoint: python3 /main.py\n"
    texto_a_escribir += "    environment:\n"
    texto_a_escribir += "      - PYTHONUNBUFFERED=1\n"
    texto_a_escribir += "      - LOGGING_LEVEL=DEBUG\n"
    texto_a_escribir += f"      - NUMBER_CLIENTS={cantidad_de_clientes}\n"
    texto_a_escribir += "    volumes:\n"
    texto_a_escribir += "      - ./server/config.ini:/server/config.ini\n"
    texto_a_escribir += "    networks:\n"
    texto_a_escribir += "      - testing_net\n\n"
    
    for i in range(1, int(cantidad_de_clientes) + 1):
        texto_a_escribir += f"  client{i}:\n"
        texto_a_escribir += f"    container_name: client{i}\n"
        texto_a_escribir += "    image: client:latest\n"
        texto_a_escribir += "    entrypoint: /client\n"
        texto_a_escribir += "    environment:\n"
        texto_a_escribir += f"      - CLI_ID={i}\n"
        texto_a_escribir += "      - CLI_LOG_LEVEL=DEBUG\n"
        texto_a_escribir += "    volumes:\n"
        texto_a_escribir += "      - ./client/config.yaml:/config.yaml\n"
        texto_a_escribir += "    networks:\n"
        texto_a_escribir += "      - testing_net\n"
        texto_a_escribir += "    depends_on:\n"
        texto_a_escribir += "      - server\n\n"

    texto_a_escribir += "networks:\n"
    texto_a_escribir += "  testing_net:\n"
    texto_a_escribir += "    ipam:\n"
    texto_a_escribir += "      driver: default\n"
    texto_a_escribir += "      config:\n"
    texto_a_escribir += "        - subnet: 172.25.125.0/24\n\n"

    with open(archivo_salida, 'w') as file:
        file.write(texto_a_escribir)


def main():
    archivo_salida = sys.argv[1]
    cantidad_de_clientes = sys.argv[2]
    generar_compose(archivo_salida, cantidad_de_clientes)


main()
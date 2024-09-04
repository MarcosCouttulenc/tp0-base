import logging

class Protocol:
    def __init__(self, socketClient):
        self.socketClient = socketClient
    
    def receiveAll(self):
        
        buffer = ""
        try:
            while True:
                data = self.socketClient.recv(1024).decode('utf-8')
                if not data:
                    break
                buffer += data
                if '\n\n' in buffer:
                    break

            addr = self.socketClient.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {buffer.strip()}')
            return buffer.strip()
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            return "Error al recibir msg"





    
    def sendAll(self, msg):

        try:
            total_sent = 0
            msg = "{}\n".format(msg).encode('utf-8')
            while total_sent < len(msg):
                sent = self.socketClient.send(msg[total_sent:])
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
                total_sent += sent
        except OSError as e:
            logging.error(f"action: send_message | result: fail | error: {e}")
        finally:
            self.socketClient.close()

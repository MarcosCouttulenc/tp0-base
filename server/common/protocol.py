import logging

class Protocol:
    def __init__(self, socketClient):
        self.socketClient = socketClient
    
    def receiveAll(self):
        try:
            msg = self.socketClient.recv(1024).rstrip().decode('utf-8')
            addr = self.socketClient.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            return msg
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
            return "Error al recibir msg"



    
    def sendAll(self, msg):
        try:
            self.socketClient.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error("action: send_message | result: fail | error: {e}")
        finally:
            self.socketClient.close()
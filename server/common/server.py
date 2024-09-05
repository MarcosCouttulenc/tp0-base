import socket
import logging
import signal
import threading
import errno

from .protocol import Protocol
from .message import BetMessage, WinnersMessage, ConfirmationMessage, WinnersResponse, getMessage
from .utils import Bet, store_bets, load_bets, has_won


class Server:
    def __init__(self, port, listen_backlog, number_clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._shutdown_event = threading.Event()
        self.number_clients = int(number_clients)
        self.confirmations = 0

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # Apenas se lanza el server, se setea el manejo de la signal SIGTERM
        # en el metodo _graceful_shutdown
        signal.signal(signal.SIGTERM, self._graceful_shutdown)



        try:
            # una vez que llegue la signal SIGTERM, el ciclo se corta           
            while not self._shutdown_event.is_set() and self.confirmations < self.number_clients:
                client_sock = self.__accept_new_connection()
                # client_sock puede ser un None si llego la SIGTERM mientras
                # el socket estaba trabado en accept(), que es lo mas probable
                # que pase siempre.
                if client_sock:
                    self.__handle_client_connection(client_sock)
        except OSError as e:
            # por si el socket levanta esta excepcion al recibir la signal SIGTERM, creo que no es necesario
            if e.errno == errno.EINTR:
                logging.info('SOCKET CERRADO - RUN')
            else:
                logging.info('Unknown exception.')
                raise
        

        logging.info('-----------TODAS LAS APUESTAS REGISTRADAS----------------------')
        # una vez que todos los clientes confirmaron que terminaron, tengo que atender a cada uno una vez para 
        # comunicarles los resultados
        
        try:
            # una vez que llegue la signal SIGTERM, el ciclo se corta           
            for i in range(self.number_clients):
                if self._shutdown_event.is_set(): break
                client_sock = self.__accept_new_connection()
                # client_sock puede ser un None si llego la SIGTERM mientras
                # el socket estaba trabado en accept(), que es lo mas probable
                # que pase siempre.
                if client_sock:
                    self.__handle_client_winners(client_sock)
        except OSError as e:
            # por si el socket levanta esta excepcion al recibir la signal SIGTERM, creo que no es necesario
            if e.errno == errno.EINTR:
                logging.info('SOCKET CERRADO - RUN')
            else:
                logging.info('Unknown exception.')
                raise


    def __handle_client_winners(self, client_sock):
        try:
            protocol = Protocol(client_sock)

            msgReceived = protocol.receiveAll()

            if msgReceived == "Error al recibir msg":
                protocol.sendAll("Error al recibir msg :(\n")
                client_sock.close()
                return

            message = getMessage(msgReceived)

            agency = message.agency

            winners = []

            for bet in load_bets():
                if has_won(bet) and int(bet.agency) == int(agency):
                    winners.append(bet.document)
            
            response = WinnersResponse(winners)

            msgToSend = response.getMessageToSend()

            logging.info(f"ENVIANDO GANADORES | msg: {msgToSend} | result: success | agency: {agency}")

            protocol.sendAll(msgToSend)

        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def _graceful_shutdown(self, signum, frame):
        logging.info(f'RECIBI SIGTERM, SE EJECUTA GRACEFUL_SHUTDOWN')
        self._shutdown_event.set()
        self._server_socket.close()  # Cerrar el socket para desbloquear accept()



    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """

        try:
            protocol = Protocol(client_sock)

            msgReceived = protocol.receiveAll()

            if msgReceived == "Error al recibir msg":
                protocol.sendAll("Error al recibir msg :(\n")
                client_sock.close()
                return

            message = getMessage(msgReceived)

            if type(message) == WinnersMessage:
                logging.info(f"TODAVIA NO TERMINARON TODOS, NO PIDAS CLIENTE: {message.agency}")
                client_sock.close()
                return
            elif type(message) == ConfirmationMessage:
                self.confirmations += 1
                logging.info(f"LLEGO CONFIRMACION DE CLIENTE: {message.agency}")
                protocol.sendAll("OK\n")
                client_sock.close()
                return

            # type(message) == BetMessage

            bets = message.createBets()

            store_bets(bets)

            cant_bets = 0
            for bet in load_bets():
                cant_bets += 1

            logging.info(f"action: apuestas_almacenadas | result: success | cantidad de apuestas: {len(bets)} | cant totales: {cant_bets}")

            protocol.sendAll("Success :)\n")
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()
        

    

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """


        logging.info('action: accept_connections | result: in_progress')
        try:
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError as e:
            if e.errno == errno.EBADF:  # Bad file descriptor, server socket closed
                logging.info('SOCKET CERRADO - ACCEPT_NEW_CONNECTIONS')
                return None
            else:
                raise

        # Connection arrived
        #logging.info('action: accept_connections | result: in_progress')
        #c, addr = self._server_socket.accept()
        #logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        #return c

import socket
import logging
import signal
import threading
import errno
import multiprocessing

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
        self.clients_procesess = []

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

        barrier = multiprocessing.Barrier(self.number_clients)
        lock = multiprocessing.Lock()




        try:
            # una vez que llegue la signal SIGTERM, el ciclo se corta           
            for i in range(self.number_clients):
                if self._shutdown_event.is_set(): break
                client_sock = self.__accept_new_connection()
                # client_sock puede ser un None si llego la SIGTERM mientras
                # el socket estaba trabado en accept(), que es lo mas probable
                # que pase siempre.
                if client_sock:
                    process = multiprocessing.Process(target=self.__handle_client_connection, args=(client_sock, barrier, lock))
                    self.clients_procesess.append(process)
                    process.start()
                    # self.__handle_client_connection(client_sock)
        except OSError as e:
            # por si el socket levanta esta excepcion al recibir la signal SIGTERM, creo que no es necesario
            if e.errno == errno.EINTR:
                logging.info('SOCKET CERRADO - RUN')
            else:
                logging.info('Unknown exception.')
                raise
        
        for process in self.clients_procesess:
            process.join()
        self.clients_procesess.clear()
        


    def __handle_client_winners(self, client_sock, lock):
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

            with lock:
                for bet in load_bets():
                    if has_won(bet) and int(bet.agency) == int(agency):
                        winners.append(bet.document)
            
            response = WinnersResponse(winners)

            msgToSend = response.getMessageToSend()

            logging.info(f"action: recibi pedido de ganadores | result: success | agency: {message.agency}")

            protocol.sendAll(msgToSend)

        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def _graceful_shutdown(self, signum, frame):
        logging.info(f'RECIBI SIGTERM, SE EJECUTA GRACEFUL_SHUTDOWN')
        self._shutdown_event.set()
        self._server_socket.close()  # Cerrar el socket para desbloquear accept()



    def __handle_client_connection(self, client_sock, barrier, lock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        

        try:
            confirmationReceived = False
            protocol = Protocol(client_sock)

            while not confirmationReceived:
                

                msgReceived = protocol.receiveAll()

                if msgReceived == "Error al recibir msg":
                    logging.info("ESTOY RECIBIENDO CON UN ERRORRRRRR")
                    protocol.sendAll("Error al recibir msg :(\n")
                    client_sock.close()
                    return

                message = getMessage(msgReceived)

                # a este no deberia entrar nunca
                if type(message) == WinnersMessage:
                    logging.info(f"action: recibi pedido de ganadores | result: fail, no estan todas las confirm | agency: {message.agency}")
                    client_sock.close()
                    return
                elif type(message) == ConfirmationMessage:
                    confirmationReceived = True
                    logging.info(f"action: recibi confirmacion de agencia: {message.agency}")
                    protocol.sendAll("OK\n")
                    break

                # type(message) == BetMessage

                bets = message.createBets()

                with lock:
                    store_bets(bets)
                    cant_bets = 0
                    for bet in load_bets():
                        cant_bets += 1

                logging.info(f"action: apuestas_almacenadas | result: success | cantidad de apuestas: {len(bets)} | cant totales: {cant_bets}")

                protocol.sendAll("Success :)\n")
            
            # sali del ciclo porque recibi la confirmacion de que termino de enviar bets
            # espero a que todos los procesos terminen con las apuestas. Solo el ultimo proceso
            # imprime el mensaje de sorteo 
            if barrier.parties - barrier.n_waiting == 1:
                logging.info("action: sorteo | result: success")    

            barrier.wait() 

            
                
            self.__handle_client_winners(client_sock, lock)

        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            #client_sock.close()
            a=2
        

    

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """


        # logging.info('action: accept_connections | result: in_progress')
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


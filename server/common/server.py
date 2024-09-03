import socket
import logging
import signal
import threading
import errno


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._shutdown_event = threading.Event()

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
            while not self._shutdown_event.is_set():
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



        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        #while True:
        #    client_sock = self.__accept_new_connection()
        #    self.__handle_client_connection(client_sock)
    

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
            # TODO: Modify the receive to avoid short-reads
            msg = client_sock.recv(1024).rstrip().decode('utf-8')
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            # TODO: Modify the send to avoid short-writes
            client_sock.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
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

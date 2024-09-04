class Message:
    def __init__(self, msg):
        params = msg.split('\n')

        self.agencia = params[0]
        self.nombre = params[1]
        self.apellido = params[2]
        self.documento = params[3]
        self.nacimiento = params[4]
        self.numero = params[5]
from .utils import Bet

PARAMS_PER_BET = 6

class Message:
    def __init__(self, msg):
        self.params = msg.split('\n')

    
    def createBets(self):
        bets = []
        numerBets = int(len(self.params) / PARAMS_PER_BET)

        for i in range(numerBets):
            agency = self.params[i*PARAMS_PER_BET]
            first_name = self.params[i*PARAMS_PER_BET + 1]
            last_name = self.params[i*PARAMS_PER_BET + 2]
            document = self.params[i*PARAMS_PER_BET + 3]
            birthdate = self.params[i*PARAMS_PER_BET + 4]
            number = self.params[i*PARAMS_PER_BET + 5]

            newBet = Bet(agency, first_name, last_name, document, birthdate, number)
            bets.append(newBet)

        return bets



from .utils import Bet

PARAMS_PER_BET = 6

class BetMessage:
    def __init__(self, params):
        self.params = params

    
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


class WinnersMessage:
    def __init__(self, agency):
        self.agency = agency

class WinnersResponse:
    def __init__(self, winners):
        self.winners = winners
    
    def getMessageToSend(self):
        msg = "\n".join(self.winners)
        msg += "\n\n"
        return msg



class ConfirmationMessage:
    def __init__(self, agency):
        self.agency = agency


def getMessage(msg):
    params = msg.split('\n')
    typeMessage = params[0]
    params.pop(0)

    if typeMessage == "BET":
        return BetMessage(params)
    elif typeMessage == "WINNERS":
        return WinnersMessage(params[0])
    elif typeMessage == "CONFIRMATION":
        return ConfirmationMessage(params[0])



        



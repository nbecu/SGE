class SGGameActions():
    def getActionPermission(aObject): #   CETTE METHODE EEST A REPRENDRE. PAS BESOIN D EPASSER PAR LA.
    #Autorisation Game Action (Create Delete Update)
        thePlayer=aObject.model.getPlayerObject(aObject.model.currentPlayer)
        authorisation=False
        theAction = None
        if thePlayer == "Admin":
            authorisation=True

        elif thePlayer is not None and thePlayer != "Admin":
            theAction=thePlayer.getGameActionOn(aObject)
            if theAction is not None:
                authorisation=theAction.checkAuthorization(aObject)
                if authorisation : 
                    theAction.incNbUsed()
                    # theAction.getRemainActionNumber(thePlayer) #  ET Pas besoin de getRemainActionNumber
        return authorisation

#  Ce serai bien de se passer de cette class GameActions
    def getMovePermission(aObject):
        thePlayer=aObject.model.getPlayerObject(aObject.model.currentPlayer)
        authorisation=False
        theAction = None
        if thePlayer == "Admin":
            authorisation=True

        elif thePlayer is not None and thePlayer != "Admin":
            theAction=thePlayer.getMooveActionOn(aObject)  
            if theAction is not None:
                authorisation=theAction.checkAuthorization(aObject)
                if authorisation :
                    theAction.incNbUsed()
        return authorisation
    

    


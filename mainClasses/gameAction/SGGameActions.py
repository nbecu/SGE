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
                authorisation=theAction.getAuthorize(aObject)
                if authorisation : 
                    theAction.use()
                    theAction.getRemainActionNumber(thePlayer) #  ET Pas besoin de getRemainActionNumber
        return authorisation

    def getMovePermission(aObject):
        thePlayer=aObject.model.getPlayerObject(aObject.model.currentPlayer)
        authorisation=False
        theAction = None
        if thePlayer == "Admin":
            authorisation=True

        elif thePlayer is not None and thePlayer != "Admin":
            theAction=thePlayer.getMooveActionOn(aObject)  
            if theAction is not None:
                authorisation=theAction.getAuthorize(aObject)
                if authorisation :
                    theAction.use()
        return authorisation
    
    def sendMqttMessage(aObject):
        aObject.model.publishEntitiesState()
    

    


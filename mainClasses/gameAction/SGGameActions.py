class SGGameActions():
    def getActionPermission(aObject):
    #Autorisation Game Action (Create Delete Update)
        thePlayer=aObject.model.getPlayerObject(aObject.model.getCurrentPlayer())
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
        return authorisation

    def getMovePermission(aObject):
        thePlayer=aObject.model.getPlayerObject(aObject.model.getCurrentPlayer())
        authorisation=False
        theAction = None
        if thePlayer == "Admin":
            authorisation=True

        elif thePlayer is not None and thePlayer != "Admin":
            theAction=thePlayer.getMooveActionOn(aObject)  
            if theAction is not None:
                authorisation=theAction.getAuthorize(aObject)
                print('ok')
                if authorisation :
                    print('ok') 
                    theAction.use()
        return authorisation
from pyaltcore import *
from components import *

@RawEvent("OnPlayerCommandText", True)
def OnCmd(playerid, text: str):
    params = text.split()
    if len(params) < 2 or len(params) > 2:
        return
    if params[0] != '/pyrestart':
        return
    
    name = params[1]

    try:
        if globalScriptManager.IsConnected(name):
            globalScriptManager.Reconnect(name)
        else:
            path = 'pyscripts/'+name+'.py'
            script = globalScriptManager.ConnectByFile(path, {"globalManager": globalManager,
                                            "globalEventManager": globalEventManager,
                                            "globalScriptManager": globalScriptManager})
            script.Run()
    except:
        Player(playerid).SendMessage("Script could not load (((")

    return True
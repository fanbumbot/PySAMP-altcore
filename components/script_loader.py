from pyaltcore import *
import os

@RawEvent("OnGameModeInit")
def OnInit():
    scriptFiles = os.listdir("pyscripts")
    for fileName in scriptFiles:
        globalScriptManager.ConnectByFile("pyscripts/"+fileName,
                                        {"globalManager": globalManager,
                                        "globalEventManager": globalEventManager,
                                        "globalScriptManager": globalScriptManager})

    globalScriptManager.Run()
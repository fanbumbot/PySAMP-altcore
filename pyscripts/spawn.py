from pyaltcore import *
from components import *

@RawEvent("OnGameModeInit")
def OnInit():
    print("Spawn script is connected!")

@RawEvent("OnPlayerRequestClass")
def OnRequest(playerid, classid):
    player: Player = globalManager.Get("Player").Get(playerid)
    player.SetSpawnInfo(1, 0.0, 0.0, 3.0, 0.0)
    player.Spawn()
from .players import *

@RawEventBefore("OnPlayerConnect")
def OnConnect(playerid):
    Player(playerid)

@RawEventAfter("OnPlayerDisconnect")
def OnDisconnect(playerid, reason):
    player: Player = Player.Get(playerid)
    player.Destroy()
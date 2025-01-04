from .players import *

@raw_event_before("OnPlayerConnect")
def on_connect(playerid):
    Player(playerid)

@raw_event_after("OnPlayerDisconnect")
def on_disconnect(playerid, reason):
    player: Player = Player.get(playerid)
    player.destroy()
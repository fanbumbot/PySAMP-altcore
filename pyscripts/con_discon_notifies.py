from pyaltcore import *
from components import *

@RawEvent("OnGameModeInit")
def OnInit():
    print("Connect-disconnect notifies script is connected!")

@RawEvent("OnPlayerConnect")
def OnConnect(playerid):
    player: Player = globalManager.Get("Player").Get(playerid)
    player.SendMessage(f"Hi, {player.Name}")

    players = Player.GetAllPlayers()
    for each_player in players:
        each_player: Player
        if each_player != player:
            each_player.SendMessage(f"Player {player.Name} connected")

@RawEvent("OnPlayerDisconnect")
def OnDisconnect(playerid, reason):
    player: Player = globalManager.Get("Player").Get(playerid)

    players = Player.GetAllPlayers()
    for each_player in players:
        each_player: Player
        if each_player != player:
            each_player.SendMessage(f"Player {player.Name} disconnected")
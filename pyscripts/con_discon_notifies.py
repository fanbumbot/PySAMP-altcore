from pyaltcore import *
from components import *

@raw_event("OnGameModeInit")
def on_init():
    print("Connect-disconnect notifies script is connected!")

@raw_event("OnPlayerConnect")
def on_connect(playerid):
    player: Player = global_manager.get("Player").get(playerid)
    player.send_message(f"Hi, {player.Name}")

    players = Player.get_all_players()
    for each_player in players:
        each_player: Player
        if each_player != player:
            each_player.send_message(f"Player {player.Name} connected")

@raw_event("OnPlayerDisconnect")
def on_disconnect(playerid, reason):
    player: Player = global_manager.get("Player").get(playerid)

    players = Player.get_all_players()
    for each_player in players:
        each_player: Player
        if each_player != player:
            each_player.send_message(f"Player {player.Name} disconnected")
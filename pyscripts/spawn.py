from pyaltcore import *
from components import *

@raw_event("OnGameModeInit")
def on_init():
    print("Spawn script is connected!")

@raw_event("OnPlayerRequestClass")
def on_request(playerid, classid):
    player: Player = global_manager.get("Player").get(playerid)
    player.set_spawn_info(1, 0.0, 0.0, 3.0, 0.0)
    player.spawn()
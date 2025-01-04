from pyaltcore import *
from components import *

all = Player.get_all_players()

for player in all:
    player: Player
    player.send_message("Hello, world")
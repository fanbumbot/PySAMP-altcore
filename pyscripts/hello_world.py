from pyaltcore import *
from components import *

all = Player.GetAllPlayers()

for player in all:
    player: Player
    player.SendMessage("Hello, world")
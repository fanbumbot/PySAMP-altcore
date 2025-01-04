from pyaltcore import *
from components import *

@raw_event_before("OnGameModeInit")
def on_init():
    Player(10000)

@raw_event("OnGameModeInit")
def on_init():
    player = Player(10000)
    for i in range(100000):
        color, old_health, new_health = player.mt_safety_test_1()
        if color % 2 == 0:
            if old_health-1 != new_health:
                print("BRUH")
        else:
            if old_health+2 != new_health:
                print("BRUH")
    print("script mt_test1 complete")
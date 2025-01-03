from pyaltcore import *
from components import *

@RawEventBefore("OnGameModeInit")
def OnInit():
    Player(10000)

@RawEvent("OnGameModeInit")
def OnInit():
    player = Player(10000)
    for i in range(100000):
        color, oldHealth, newHealth = player.MTSafetyTest1()
        if color % 2 == 0:
            if oldHealth-1 != newHealth:
                print("BRUH")
        else:
            if oldHealth+2 != newHealth:
                print("BRUH")
    print("script mt_test1 complete")
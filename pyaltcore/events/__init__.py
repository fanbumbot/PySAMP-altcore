from .event_leaded_thread import *
from .event_manager import *

import threading

predefinedCallbacks = set((
    'OnGameModeInit',
    'OnGameModeExit',
    'OnActorStreamIn',
    'OnActorStreamOut',
    'OnClientCheckResponse',
    'OnDialogResponse',
    'OnEnterExitModShop',
    'OnIncomingConnection',
    'OnObjectMoved',
    'OnPlayerClickMap',
    'OnPlayerClickPlayer',
    'OnPlayerClickPlayerTextDraw',
    'OnPlayerClickTextDraw',
    'OnPlayerCommandText',
    'OnPlayerConnect',
    'OnPlayerDeath',
    'OnPlayerDisconnect',
    'OnPlayerEditAttachedObject',
    'OnPlayerEditObject',
    'OnPlayerEnterCheckpoint',
    'OnPlayerEnterRaceCheckpoint',
    'OnPlayerEnterVehicle',
    'OnPlayerExitVehicle',
    'OnPlayerExitedMenu',
    'OnPlayerGiveDamage',
    'OnPlayerGiveDamageActor',
    'OnPlayerInteriorChange',
    'OnPlayerKeyStateChange',
    'OnPlayerLeaveCheckpoint',
    'OnPlayerLeaveRaceCheckpoint',
    'OnPlayerObjectMoved',
    'OnPlayerPickUpPickup',
    'OnPlayerRequestClass',
    'OnPlayerRequestSpawn',
    'OnPlayerSelectObject',
    'OnPlayerSelectedMenuRow',
    'OnPlayerSpawn',
    'OnPlayerStateChange',
    'OnPlayerStreamIn',
    'OnPlayerStreamOut',
    'OnPlayerTakeDamage',
    'OnPlayerText',
    'OnPlayerUpdate',
    'OnPlayerWeaponShot',
    'OnRconCommand',
    'OnRconLoginAttempt',
    'OnTrailerUpdate',
    'OnUnoccupiedVehicleUpdate',
    'OnVehicleDamageStatusUpdate',
    'OnVehicleDeath',
    'OnVehicleMod',
    'OnVehiclePaintjob',
    'OnVehicleRespray',
    'OnVehicleSirenStateChange',
    'OnVehicleSpawn',
    'OnVehicleStreamIn',
    'OnVehicleStreamOut',
))

def RawEvent(name: str, waitResult: bool = False, resultWithoutWaiting = None):
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        currentThread = threading.current_thread()
        globalEventManager.Subscribe(name, func, currentThread, waitResult,
                                     resultWithoutWaiting)
        return wrapper
    return my_decorator

def RawEventBefore(name: str, waitResult: bool = False, resultWithoutWaiting = None):
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        currentThread = threading.current_thread()
        globalEventManager.Subscribe(name, func, currentThread, waitResult,
                                     resultWithoutWaiting, True)
        return wrapper
    return my_decorator

def RawEventAfter(name: str, waitResult: bool = False, resultWithoutWaiting = None):
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        currentThread = threading.current_thread()
        globalEventManager.Subscribe(name, func, currentThread, waitResult,
                                     resultWithoutWaiting, isAfter=True)
        return wrapper
    return my_decorator

for name in predefinedCallbacks:
    defaultValue = 1
    match name:
        case "OnDialogResponse" | "OnPlayerCommandText":
            defaultValue = 0
    globalEventManager.RegisterPredefinedEvent(name, defaultValue)
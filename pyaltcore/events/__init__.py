from .event_leaded_thread import *
from .event_manager import *

import threading

predefined_callbacks = set((
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

def raw_event(name: str, wait_result: bool = False, result_without_waiting = None):
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        currentThread = threading.current_thread()
        global_event_manager.subscribe(name, func, currentThread, wait_result,
                                     result_without_waiting)
        return wrapper
    return my_decorator

def raw_event_before(name: str, wait_result: bool = False, result_without_waiting = None):
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        current_thread = threading.current_thread()
        global_event_manager.subscribe(name, func, current_thread, wait_result,
                                     result_without_waiting, True)
        return wrapper
    return my_decorator

def raw_event_after(name: str, wait_result: bool = False, result_without_waiting = None):
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        current_thread = threading.current_thread()
        global_event_manager.subscribe(name, func, current_thread, wait_result,
                                     result_without_waiting, is_after=True)
        return wrapper
    return my_decorator

for name in predefined_callbacks:
    default_value = 1
    match name:
        case "OnDialogResponse" | "OnPlayerCommandText":
            default_value = 0
    global_event_manager.register_predefined_event(name, default_value)
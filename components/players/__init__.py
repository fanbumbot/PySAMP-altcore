from pyaltcore import *
from samp import *

class BasePlayer(GlobalObject):
    def __init__(self, id: int):
        super().__init__(id)
        self.health = 100
        self.armour = 100

    def destroy(self):
        return super().destroy()

    def is_connected(self) -> bool:
        return IsPlayerConnected(self.id)

    @property
    def ID(self) -> int:
        return self.id

    @property
    def Health(self) -> int:
        return self.health
    
    @Health.setter
    def Health(self, health: int):
        self.health = health
    
    @property
    def Armour(self) -> int:
        return self.armour
    
    def send_message(self, message: str):
        SendClientMessage(self.ID, -1, message)

    def spawn(self):
        SpawnPlayer(self.ID)

    def set_spawn_info(self, skin: int, x: float, y: float, z: float, rz: float):
        SetSpawnInfo(self.ID, 0, skin, x, y, z, rz, 0, 0, 0, 0, 0, 0)

    @classmethod
    @mtsafe_class_method
    def get_all_players(cls) -> list["BasePlayer"]:
        return global_manager.get("Player").get_all().values()
    
global_manager.add("Player", BasePlayer)

class Player(BasePlayer):
    def __init__(self, id):
        super().__init__(id)
        self.skin = 0
        self.color = 0
        
        if self.is_connected():
            self.name = GetPlayerName(self.id)
        else:
            self.name = ""

    @property
    def Skin(self) -> int:
        return self.skin
    
    @Skin.setter
    def Skin(self, skin: int):
        self.skin = skin

    @property
    def Color(self) -> int:
        return self.color
    
    @Color.setter
    def Color(self, color: int):
        self.color = color

    @property
    def Name(self) -> str:
        return self.name
    
    @Name.setter
    def Name(self, name: str):
        self.name = name
    
    def mt_safety_test_1(self):
        old_health = self.health
        self.color += 1
        if self.color % 2 == 0:
            self.health -= 1
        else:
            self.health += 2
        return self.color, old_health, self.health

global_manager.add("Player", Player)
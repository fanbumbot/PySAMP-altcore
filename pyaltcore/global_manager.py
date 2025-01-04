from .mt_safe_class import MTSafeClass

class IID:
    def __init__(self, id):
        super().__init__()
        self.id = id

    @property
    def ID(self):
        return self.id

# Pass item by name
class ContainerByName:
    def __init__(self):
        self.container = dict()

    def __iter__(self):
        return self.container.__iter__()

    def is_contained(self, name):
        return name in self.container
    
    def add(self, name, item):
        self.container[name] = item

    def remove(self, name):
        if self.is_contained(name):
            del self.container[name]

    def get(self, name):
        if self.is_contained(name):
            return self.container[name]
        
    def get_all(self):
        return self.container.copy()
    
class MTSafeContainerByName(ContainerByName, MTSafeClass):
    pass

class GlobalClass(MTSafeContainerByName):
    def __init__(self, type_class: "GlobalObject"):
        super().__init__()
        self.type_class = type_class

    def destroy(self):
        for objName in self:
            obj: "GlobalObject" = self.get(objName)
            obj.destroy()

    def add(self, name, obj: "GlobalObject"):
        super().add(name, obj)

    def remove(self, name):
        super().remove(name)

class GlobalClassManager(MTSafeContainerByName):
    def add(self, name, item: "GlobalObject"):
        if self.is_contained(name):# replacing
            self.remove(name)
        super().add(name, GlobalClass(item))
        GlobalObject.global_class_ref[item] = name

    def remove(self, name):
        if self.is_contained(name):
            global_class: GlobalClass = self.get(name)
            global_class.destroy()
            super().remove(name)

    def get(self, name) -> GlobalClass:
        return super().get(name)

global_manager = GlobalClassManager()

class GlobalObject(IID, MTSafeClass):
    global_class_ref: dict[type, str] = dict()

    def __new__(cls, id):
        global_class = cls.get_global_class()
        if global_class.is_contained(id):
            return global_class.get(id)
        return super().__new__(cls)

    def __init__(self, id):
        IID.__init__(self, id)
        global_class = self.__class__.get_global_class()
        if global_class != None:
            global_class.add(id, self)

    def destroy(self):
        global_class = self.__class__.get_global_class()
        global_class.remove(self.ID)

    @classmethod
    def get(cls, id):
        global_class = cls.get_global_class()
        if global_class == None or (not global_class.is_contained(id)):
            return None
        return global_class.get(id)
    
    @classmethod
    def get_all(cls):
        global_class = cls.get_global_class()
        if global_class != None:
            return global_class.get_all()

    @classmethod
    def get_global_class(cls) -> GlobalClass:
        if cls in GlobalObject.global_class_ref:
            name = GlobalObject.global_class_ref[cls]
            if global_manager.is_contained(name):
                return global_manager.get(name)
        return None
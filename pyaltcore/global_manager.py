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

    def IsContained(self, name):
        return name in self.container
    
    def Add(self, name, item):
        self.container[name] = item

    def Remove(self, name):
        if self.IsContained(name):
            del self.container[name]

    def Get(self, name):
        if self.IsContained(name):
            return self.container[name]
        
    def GetAll(self):
        return self.container.copy()
    
class MTSafeContainerByName(ContainerByName, MTSafeClass):
    pass

class GlobalClass(MTSafeContainerByName):
    def __init__(self, typeClass: "GlobalObject"):
        super().__init__()
        self.typeClass = typeClass

    def Destroy(self):
        for objName in self:
            obj: "GlobalObject" = self.Get(objName)
            obj.Destroy()

    def Add(self, name, obj: "GlobalObject"):
        super().Add(name, obj)

    def Remove(self, name):
        super().Remove(name)

class GlobalClassManager(MTSafeContainerByName):
    def Add(self, name, item: "GlobalObject"):
        if self.IsContained(name):# replacing
            self.Remove(name)
        super().Add(name, GlobalClass(item))
        GlobalObject.global_class_ref[item] = name

    def Remove(self, name):
        if self.IsContained(name):
            globalClass: GlobalClass = self.Get(name)
            globalClass.Destroy()
            super().Remove(name)

    def Get(self, name) -> GlobalClass:
        return super().Get(name)

globalManager = GlobalClassManager()

class GlobalObject(IID, MTSafeClass):
    global_class_ref: dict[type, str] = dict()

    def __new__(cls, id):
        globalClass = cls.GetGlobalClass()
        if globalClass.IsContained(id):
            return globalClass.Get(id)
        return super().__new__(cls)

    def __init__(self, id):
        IID.__init__(self, id)
        globalClass = self.__class__.GetGlobalClass()
        if globalClass != None:
            globalClass.Add(id, self)

    def Destroy(self):
        globalClass = self.__class__.GetGlobalClass()
        globalClass.Remove(self.ID)

    @classmethod
    def Get(cls, id):
        globalClass = cls.GetGlobalClass()
        if globalClass == None or (not globalClass.IsContained(id)):
            return None
        return globalClass.Get(id)
    
    @classmethod
    def GetAll(cls):
        globalClass = cls.GetGlobalClass()
        if globalClass != None:
            return globalClass.GetAll()

    @classmethod
    def GetGlobalClass(cls) -> GlobalClass:
        if cls in GlobalObject.global_class_ref:
            name = GlobalObject.global_class_ref[cls]
            if globalManager.IsContained(name):
                globalClass = globalManager.Get(name)
                return globalClass
        return None
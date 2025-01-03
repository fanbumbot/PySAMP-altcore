from typing import Callable, Any
import threading

MT_LOCK_NAME = '__mt_lock'

SELF_ATTR_NAME = 'self'
INIT_FUNC_NAME = '__init__'
GET_ATTR_FUNC_NAME = '__getattribute__'
SET_ATTR_FUNC_NAME = '__setattr__'

reservedObjectClassNames = set((
    INIT_FUNC_NAME,
    GET_ATTR_FUNC_NAME,
    SET_ATTR_FUNC_NAME,
    '__class__',
    '__dict__'
))

def InitOverriding(overriddenClass):
    setattr(overriddenClass, INIT_FUNC_NAME, MTSafeInit(overriddenClass.__init__))

def GetOverriding(overriddenClass):
    setattr(overriddenClass, GET_ATTR_FUNC_NAME, MTSafeGet(overriddenClass.__getattribute__))

def SetOverriding(overriddenClass):
    setattr(overriddenClass, SET_ATTR_FUNC_NAME, MTSafeSet(overriddenClass.__setattr__))

def GetSetInitOverriding(overriddenClass, overrideGetSet):
    oldInit = overriddenClass.__init__
    if not isinstance(oldInit, MTSafeInit):
        InitOverriding(overriddenClass)

    if overrideGetSet:
        oldGet = overriddenClass.__getattribute__
        if not isinstance(oldGet, MTSafeGet):
            GetOverriding(overriddenClass)

        oldSet = overriddenClass.__setattr__
        if not isinstance(oldSet, MTSafeSet):
            SetOverriding(overriddenClass)

class MTSafeObject:
    def __init__(self):
        pass

class MTSafeSelfFunc(MTSafeObject):
    def __init__(self, func: Callable):
        self.func = func
        self.objectSelf = None

    def __get__(self, instance, owner):
        self.objectSelf = instance
        return self

    def __call__(__thisSelf, *args, **kwds):
        if __thisSelf.objectSelf == None:
            if SELF_ATTR_NAME in kwds:
                __thisSelf.objectSelf = kwds[SELF_ATTR_NAME]
                del kwds[SELF_ATTR_NAME]
            else:
                __thisSelf.objectSelf = args[0]
                args = args[1:]
        with getattr(__thisSelf.objectSelf, MT_LOCK_NAME):
            #print("CALLED", __thisSelf.func)
            return __thisSelf.func(__thisSelf.objectSelf, *args, **kwds)

class MTSafeInit(MTSafeObject):
    def __init__(self, originalInit: Callable):
        self.originalInit = originalInit
        self.objectSelf = None

    def __get__(self, instance, owner):
        self.objectSelf = instance
        return self

    def __call__(__thisSelf, *args, **kwds):
        setattr(__thisSelf.objectSelf, MT_LOCK_NAME, threading.RLock())
        __thisSelf.originalInit(__thisSelf.objectSelf, *args, **kwds)
        #print("LOCKED", object)

class MTSafeGet(MTSafeObject):
    def __init__(self, originalGet: Callable):
        self.originalGet = originalGet
        self.objectSelf = None

    def __get__(self, instance, owner):
        self.objectSelf = instance
        return self

    def __call__(__thisSelf, *args):
        if __thisSelf.objectSelf == None:
            __thisSelf.objectSelf = args[0]
        name = args[0]
        if name == GET_ATTR_FUNC_NAME:
            return __thisSelf.originalGet
        if name == MT_LOCK_NAME:
            return __thisSelf.originalGet(__thisSelf.objectSelf, MT_LOCK_NAME)
        with __thisSelf.originalGet(__thisSelf.objectSelf, MT_LOCK_NAME):
            #print("GET", __thisSelf.objectSelf, name)
            return __thisSelf.originalGet(__thisSelf.objectSelf, name)
        
class MTSafeSet(MTSafeObject):
    def __init__(self, originalSet: Callable):
        self.originalSet = originalSet
        self.objectSelf = None

    def __get__(self, instance, owner):
        self.objectSelf = instance
        return self

    def __call__(__thisSelf, *args):
        if __thisSelf.objectSelf == None:
            __thisSelf.objectSelf = args[0]
        name = args[0]
        value = args[1]
        if name == MT_LOCK_NAME:
            return __thisSelf.originalSet(__thisSelf.objectSelf, name, value)
        with getattr(__thisSelf.objectSelf, MT_LOCK_NAME):
            #print("SET", __thisSelf.objectSelf, name, value)
            return __thisSelf.originalSet(__thisSelf.objectSelf, name, value)

def SubClassesRewrite(mainClass):
    rewrittenClasses = set()
    def Recursive(subclass):
        global reservedObjectClassNames
        nonlocal rewrittenClasses

        rewrittenClasses.add(subclass)

        for basedClass in subclass.__bases__:
            if basedClass in rewrittenClasses or basedClass == object or basedClass == MTSafeClass:
                continue
            if issubclass(basedClass, MTSafeClass):
                rewrittenClasses.add(basedClass)
                continue

            Recursive(basedClass)

        for name in subclass.__dict__:
            attribute = subclass.__dict__[name]
            if isinstance(attribute, MTSafeObject):
                continue
            
            if not (name in reservedObjectClassNames):
                if (isinstance(attribute, Callable) and 
                        not (isinstance(attribute, staticmethod) or 
                            isinstance(attribute, classmethod))):
                    attribute = MTSafeSelfFunc(attribute)
            else:
                continue

            setattr(mainClass, name, attribute)
    Recursive(mainClass)

def MTSafeClassSelf(mainClass: type):
    SubClassesRewrite(mainClass)
    GetSetInitOverriding(mainClass, True)
    return mainClass

def MTSafeClassFunc(mainClass: type):
    MTSafeClassSelf(mainClass)
    return mainClass

class MTSafeClass:
    def __init__(self):
        pass
    def __init_subclass__(cls):
        setattr(cls, MT_LOCK_NAME, threading.RLock())
        return MTSafeClassFunc(cls)
    
    @classmethod
    def ClassLock(cls) -> threading.RLock:
        return getattr(cls, MT_LOCK_NAME)
    
def MTSafeClassMethod(func):
    def MTSafeMethod(cls, *args, **kwargs):
        with getattr(cls, MT_LOCK_NAME):
            return func(cls, *args, **kwargs)
    return MTSafeMethod
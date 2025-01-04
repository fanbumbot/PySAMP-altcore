from typing import Callable, Any
import threading

MT_LOCK_NAME = '__mt_lock'

SELF_ATTR_NAME = 'self'
INIT_FUNC_NAME = '__init__'
GET_ATTR_FUNC_NAME = '__getattribute__'
SET_ATTR_FUNC_NAME = '__setattr__'

reserved_object_class_names = set((
    INIT_FUNC_NAME,
    GET_ATTR_FUNC_NAME,
    SET_ATTR_FUNC_NAME,
    '__class__',
    '__dict__'
))

def init_overriding(overridden_class):
    setattr(overridden_class, INIT_FUNC_NAME, MTSafeInit(overridden_class.__init__))

def get_overriding(overridden_class):
    setattr(overridden_class, GET_ATTR_FUNC_NAME, MTSafeGet(overridden_class.__getattribute__))

def set_overriding(overridden_class):
    setattr(overridden_class, SET_ATTR_FUNC_NAME, MTSafeSet(overridden_class.__setattr__))

def get_set_init_overriding(overridden_class, override_get_set: bool):
    old_init = overridden_class.__init__
    if not isinstance(old_init, MTSafeInit):
        init_overriding(overridden_class)

    if override_get_set:
        old_get = overridden_class.__getattribute__
        if not isinstance(old_get, MTSafeGet):
            get_overriding(overridden_class)

        old_set = overridden_class.__setattr__
        if not isinstance(old_set, MTSafeSet):
            set_overriding(overridden_class)

class MTSafeObject:
    def __init__(self):
        pass

class MTSafeSelfFunc(MTSafeObject):
    def __init__(self, func: Callable):
        self.func = func
        self.object_self = None

    def __get__(self, instance, owner):
        self.object_self = instance
        return self

    def __call__(this_self, *args, **kwds):
        if this_self.object_self == None:
            if SELF_ATTR_NAME in kwds:
                this_self.object_self = kwds[SELF_ATTR_NAME]
                del kwds[SELF_ATTR_NAME]
            else:
                this_self.object_self = args[0]
                args = args[1:]
        with getattr(this_self.object_self, MT_LOCK_NAME):
            #print("CALLED", this_self.func)
            return this_self.func(this_self.object_self, *args, **kwds)

class MTSafeInit(MTSafeObject):
    def __init__(self, original_init: Callable):
        self.original_init = original_init
        self.object_self = None

    def __get__(self, instance, owner):
        self.object_self = instance
        return self

    def __call__(this_self, *args, **kwds):
        setattr(this_self.object_self, MT_LOCK_NAME, threading.RLock())
        this_self.original_init(this_self.object_self, *args, **kwds)
        #print("LOCKED", object)

class MTSafeGet(MTSafeObject):
    def __init__(self, original_get: Callable):
        self.original_get = original_get
        self.object_self = None

    def __get__(self, instance, owner):
        self.object_self = instance
        return self

    def __call__(this_self, *args):
        if this_self.object_self == None:
            this_self.object_self = args[0]
        name = args[0]
        if name == GET_ATTR_FUNC_NAME:
            return this_self.original_get
        if name == MT_LOCK_NAME:
            return this_self.original_get(this_self.object_self, MT_LOCK_NAME)
        with this_self.original_get(this_self.object_self, MT_LOCK_NAME):
            #print("GET", this_self.object_self, name)
            return this_self.original_get(this_self.object_self, name)
        
class MTSafeSet(MTSafeObject):
    def __init__(self, original_set: Callable):
        self.original_set = original_set
        self.object_self = None

    def __get__(self, instance, owner):
        self.object_self = instance
        return self

    def __call__(__this_self, *args):
        if __this_self.object_self == None:
            __this_self.object_self = args[0]
        name = args[0]
        value = args[1]
        if name == MT_LOCK_NAME:
            return __this_self.original_set(__this_self.object_self, name, value)
        with getattr(__this_self.object_self, MT_LOCK_NAME):
            #print("SET", __this_self.object_self, name, value)
            return __this_self.original_set(__this_self.object_self, name, value)

def subclasses_rewrite(main_class):
    rewritten_classes = set()
    def recursive(subclass):
        global reserved_object_class_names
        nonlocal rewritten_classes

        rewritten_classes.add(subclass)

        for based_class in subclass.__bases__:
            if based_class in rewritten_classes or based_class == object or based_class == MTSafeClass:
                continue
            if issubclass(based_class, MTSafeClass):
                rewritten_classes.add(based_class)
                continue

            recursive(based_class)

        for name in subclass.__dict__:
            attribute = subclass.__dict__[name]
            if isinstance(attribute, MTSafeObject):
                continue
            
            if not (name in reserved_object_class_names):
                if (isinstance(attribute, Callable) and 
                        not (isinstance(attribute, staticmethod) or 
                            isinstance(attribute, classmethod))):
                    attribute = MTSafeSelfFunc(attribute)
            else:
                continue

            setattr(main_class, name, attribute)
    recursive(main_class)

def mtsafe_class_self(main_class: type):
    subclasses_rewrite(main_class)
    get_set_init_overriding(main_class, True)
    return main_class

def mtsafe_class_func(main_class: type):
    mtsafe_class_self(main_class)
    return main_class

class MTSafeClass:
    def __init__(self):
        pass
    def __init_subclass__(cls):
        setattr(cls, MT_LOCK_NAME, threading.RLock())
        return mtsafe_class_func(cls)
    
    @classmethod
    def class_lock(cls) -> threading.RLock:
        return getattr(cls, MT_LOCK_NAME)
    
def mtsafe_class_method(func):
    def mtsafe_method(cls, *args, **kwargs):
        with getattr(cls, MT_LOCK_NAME):
            return func(cls, *args, **kwargs)
    return mtsafe_method
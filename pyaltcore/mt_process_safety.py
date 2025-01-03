"""
Replacing all functions from __init__.pyi (samp) with
multithreading safety

Is it necessary to do exception for natives?
"""

import samp
import threading

from types import BuiltinFunctionType
from typing import Callable

callNativeEvent = threading.Event()
callNativeEvent.set()

def EventProc(event: threading.Event, func: Callable, *args, **kwargs):
    event.wait()
    event.clear()
    answer = func(*args, **kwargs)
    event.set()
    return answer

def ReplaceFunc(name: str, func: Callable):
    samp.__dict__[name] = lambda *args, **kwargs: HandlerReplacedFunc(func, *args, **kwargs)

def HandlerReplacedFunc(func: Callable, *args, **kwargs):
    global callNativeEvent
    return EventProc(callNativeEvent, func, *args, **kwargs)

for name in samp.__dict__:
    func = samp.__dict__[name]
    
    if isinstance(func, BuiltinFunctionType):
        ReplaceFunc(name, func)

from samp import *
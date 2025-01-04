"""
Replacing all functions from __init__.pyi (samp) with
multithreading safety

Is it necessary to do exception for natives?
"""

import samp
import threading

from types import BuiltinFunctionType
from typing import Callable

call_native_event = threading.Event()
call_native_event.set()

def event_proc(event: threading.Event, func: Callable, *args, **kwargs):
    event.wait()
    event.clear()
    answer = func(*args, **kwargs)
    event.set()
    return answer

def replace_func(name: str, func: Callable):
    samp.__dict__[name] = lambda *args, **kwargs: handler_replaced_func(func, *args, **kwargs)

def handler_replaced_func(func: Callable, *args, **kwargs):
    global call_native_event
    return event_proc(call_native_event, func, *args, **kwargs)

for name in samp.__dict__:
    func = samp.__dict__[name]
    
    if isinstance(func, BuiltinFunctionType):
        replace_func(name, func)

from samp import *
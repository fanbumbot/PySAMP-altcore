import threading
from queue import Queue
from typing import Callable

from dataclasses import dataclass

@dataclass
class TransferPacket:
    pass

@dataclass
class FunctionTransferPacket(TransferPacket):
    event: threading.Event
    func: Callable
    args: tuple
    kwargs: tuple

@dataclass
class CodeTransferPacket(TransferPacket):
    code: str
    globalScope: dict

class EventLeadedThread(threading.Thread):
    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.queue = Queue()
        self.pause = False
        self.destroyed = False
        self.result = None
        self.readyEvent = threading.Event()
        self.allLock = threading.Lock()

    def PutFunc(self, event: threading.Event, func, args, kwargs):
        with self.allLock:
            self.queue.put(FunctionTransferPacket(event, func, args, kwargs))
            if (not self.pause) and (not self.destroyed):
                self.readyEvent.set()

    def PutCode(self, code: str, globalScope: dict):
        with self.allLock:
            self.queue.put(CodeTransferPacket(code, globalScope))
            if (not self.pause) and (not self.destroyed):
                self.readyEvent.set()

    def GetResult(self):
        with self.allLock:
            return self.result

    def run(self):
        while not self.destroyed:
            self.readyEvent.wait()
            if self.queue.empty() or self.destroyed:
                continue

            transferPacket: TransferPacket = self.queue.get()
            if isinstance(transferPacket, FunctionTransferPacket):
                self.result = transferPacket.func(*transferPacket.args, **transferPacket.kwargs)
                if transferPacket.event != None:
                    transferPacket.event.set()
            elif isinstance(transferPacket, CodeTransferPacket):
                exec(transferPacket.code, transferPacket.globalScope)

            if self.queue.empty():
                self.readyEvent.clear()

    def Stop(self):
        with self.allLock:
            self.pause = True
            self.readyEvent.clear()

    def Start(self):
        with self.allLock:
            self.pause = False
            if not self.queue.empty():
                self.readyEvent.set()

    def Destroy(self):
        with self.allLock:
            self.destroyed = True
            self.readyEvent.set()

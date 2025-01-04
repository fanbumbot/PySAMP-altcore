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
    global_scope: dict

class EventLeadedThread(threading.Thread):
    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.queue = Queue()
        self.pause = False
        self.destroyed = False
        self.result = None
        self.ready_event = threading.Event()
        self.all_lock = threading.Lock()

    def put_func(self, event: threading.Event, func, args, kwargs):
        with self.all_lock:
            self.queue.put(FunctionTransferPacket(event, func, args, kwargs))
            if (not self.pause) and (not self.destroyed):
                self.ready_event.set()

    def put_code(self, code: str, global_scope: dict):
        with self.all_lock:
            self.queue.put(CodeTransferPacket(code, global_scope))
            if (not self.pause) and (not self.destroyed):
                self.ready_event.set()

    def get_result(self):
        with self.all_lock:
            return self.result

    def run(self):
        while not self.destroyed:
            self.ready_event.wait()
            if self.queue.empty() or self.destroyed:
                continue

            transfer_packet: TransferPacket = self.queue.get()
            if isinstance(transfer_packet, FunctionTransferPacket):
                self.result = transfer_packet.func(*transfer_packet.args, **transfer_packet.kwargs)
                if transfer_packet.event != None:
                    transfer_packet.event.set()
            elif isinstance(transfer_packet, CodeTransferPacket):
                exec(transfer_packet.code, transfer_packet.global_scope)

            if self.queue.empty():
                self.ready_event.clear()

    def stop(self):
        with self.all_lock:
            self.pause = True
            self.ready_event.clear()

    def start(self):
        with self.all_lock:
            self.pause = False
            if not self.queue.empty():
                self.ready_event.set()
        super().start()

    def destroy(self):
        with self.all_lock:
            self.destroyed = True
            self.ready_event.set()

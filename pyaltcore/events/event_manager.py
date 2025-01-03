from samp import RegisterCallback

from .event_leaded_thread import EventLeadedThread, threading

from typing import Callable, Any

class EventSubscribeException(Exception):
    pass

class EventManager:
    def __init__(self):
        self.__all_handlers: dict[str, list[tuple[Callable, EventLeadedThread, bool, Any]]] = dict()
        self.__all_handlers_before: dict[str, list[tuple[Callable, EventLeadedThread, bool, Any]]] = dict()
        self.__all_handlers_after: dict[str, list[tuple[Callable, EventLeadedThread, bool, Any]]] = dict()
        self.resultWaitEvent: threading.Event = threading.Event()

        self.unsubscribeLock = threading.Lock()

    def RegisterPredefinedEvent(self, name: str, defaultValue: int = 1):
        self.__make_mark(name, lambda *args, **kwargs: self.Handler(name, defaultValue, args, kwargs))
        if not (name in self.__all_handlers):
            self.__all_handlers[name] = list()
            self.__all_handlers_before[name] = list()
            self.__all_handlers_after[name] = list()

    def RegisterNewEvent(self, name: str, parameter_types: str, defaultValue: int = 1):
        RegisterCallback(name, parameter_types)
        self.RegisterPredefinedEvent(name, defaultValue)

    def UnregisterEvent(self, name: str):
        if not (name in self.__all_handlers):
            return
        del self.__all_handlers[name]
        self.__class__.__remove_mark(name)

    @staticmethod
    def __make_mark(name: str, func: Callable):
        """
            Add 'port' on plugin-python-plugin level
        """
        import python
        setattr(python, name, func)

    @staticmethod
    def __remove_mark(name: str):
        """
            Remove 'port' on plugin-python-plugin level
        """
        import python
        delattr(python, name)

    def Subscribe(self, name: str, func: Callable,
                  thread: EventLeadedThread, waitResult: bool,
                  resultWithoutWaiting = None,
                  isBefore:bool = False, isAfter: bool = False):
        if (not (name in self.__all_handlers) or
            not (name in self.__all_handlers_before) or
            not (name in self.__all_handlers_after)):
            raise EventSubscribeException(f"Event with the name '{name}' is not exists")
        if isBefore:
            self.__all_handlers_before[name].append((func, thread, waitResult, resultWithoutWaiting))
        elif isAfter:
            self.__all_handlers_after[name].append((func, thread, waitResult, resultWithoutWaiting))
        else:
            self.__all_handlers[name].append((func, thread, waitResult, resultWithoutWaiting))

    def Unsubscribe(self, name: str, func: Callable, thread: EventLeadedThread):
        with self.unsubscribeLock:
            if not (name in self.__all_handlers):
                return
            try:
                for i in range(len(self.__all_handlers[name])):
                    iterFunc, iterThread, _, _ = self.__all_handlers[name]
                    if iterFunc == func and iterThread == thread:
                        del self.__all_handlers[name][i]
                        break
            except:
                raise EventSubscribeException(f"Function '{func.__name__}' is not subscribed on event '{name}'")

    def ClearSubscribesByName(self, name: str):
        with self.unsubscribeLock:
            if name in self.__all_handlers:
                self.__all_handlers[name].clear()
            if name in self.__all_handlers_before:
                self.__all_handlers_before[name].clear()
            if name in self.__all_handlers_after:
                self.__all_handlers_after[name].clear()

    def ClearSubscribesByThread(self, thread: EventLeadedThread):
        def ClearInLoop(container):
            for nameEvent in container:
                i = 0
                while i < len(container[nameEvent]):
                    _, iterThread, _, _ = container[nameEvent][i]
                    if iterThread == thread:
                        del container[nameEvent][i]
                    else:
                        i += 1
        ClearInLoop(self.__all_handlers)
        ClearInLoop(self.__all_handlers_before)
        ClearInLoop(self.__all_handlers_after)

    def Handler(self, name: str, defaultValue: int, args, kwargs):
        def Loop(iterator, forceWait = True):
            for func, thread, waitResult, resultWithoutWaiting in iterator:
                if isinstance(thread, EventLeadedThread):
                    if waitResult or forceWait:
                        self.resultWaitEvent.clear()
                        thread.PutFunc(self.resultWaitEvent, func, args, kwargs)
                        self.resultWaitEvent.wait()
                        answer = thread.GetResult()
                    else:
                        thread.PutFunc(None, func, args, kwargs)
                        answer = resultWithoutWaiting
                else:
                    answer = func(*args, **kwargs)
                if (answer != None) and (answer != defaultValue):
                    return answer
            return defaultValue
                
        if name in self.__all_handlers_before:
            Loop(self.__all_handlers_before[name], True)

        if not (name in self.__all_handlers):
            answer = defaultValue
        else:
            answer = Loop(self.__all_handlers[name])

        if name in self.__all_handlers_after:
            Loop(self.__all_handlers_after[name])

        return answer

globalEventManager = EventManager()
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
        self.result_wait_event: threading.Event = threading.Event()

        self.unsubscribe_lock = threading.Lock()

    def register_predefined_event(self, name: str, default_value: int = 1):
        self.__make_mark(name, lambda *args, **kwargs: self.handler(name, default_value, args, kwargs))
        if not (name in self.__all_handlers):
            self.__all_handlers[name] = list()
            self.__all_handlers_before[name] = list()
            self.__all_handlers_after[name] = list()

    def register_new_event(self, name: str, parameter_types: str, default_value: int = 1):
        RegisterCallback(name, parameter_types)
        self.register_predefined_event(name, default_value)

    def unregister_event(self, name: str):
        if not (name in self.__all_handlers):
            return
        del self.__all_handlers[name]
        del self.__all_handlers_before[name]
        del self.__all_handlers_after[name]
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

    def subscribe(self, name: str, func: Callable,
                  thread: EventLeadedThread, wait_result: bool,
                  result_without_waiting = None,
                  is_before:bool = False, is_after: bool = False):
        if (not (name in self.__all_handlers) or
            not (name in self.__all_handlers_before) or
            not (name in self.__all_handlers_after)):
            raise EventSubscribeException(f"Event with the name '{name}' is not exists")
        if is_before:
            self.__all_handlers_before[name].append((func, thread, wait_result, result_without_waiting))
        elif is_after:
            self.__all_handlers_after[name].append((func, thread, wait_result, result_without_waiting))
        else:
            self.__all_handlers[name].append((func, thread, wait_result, result_without_waiting))

    def unsubscribe(self, name: str, func: Callable, thread: EventLeadedThread):
        with self.unsubscribe_lock:
            if not (name in self.__all_handlers):
                return
            try:
                for i in range(len(self.__all_handlers[name])):
                    iter_func, iter_thread, _, _ = self.__all_handlers[name]
                    if iter_func == func and iter_thread == thread:
                        del self.__all_handlers[name][i]
                        break
            except:
                raise EventSubscribeException(f"Function '{func.__name__}' is not subscribed on event '{name}'")

    def clear_subscribes_by_name(self, name: str):
        with self.unsubscribe_lock:
            if name in self.__all_handlers:
                self.__all_handlers[name].clear()
            if name in self.__all_handlers_before:
                self.__all_handlers_before[name].clear()
            if name in self.__all_handlers_after:
                self.__all_handlers_after[name].clear()

    def clear_subscribes_by_thread(self, thread: EventLeadedThread):
        def clear_in_loop(container):
            for name_event in container:
                i = 0
                while i < len(container[name_event]):
                    _, iter_thread, _, _ = container[name_event][i]
                    if iter_thread == thread:
                        del container[name_event][i]
                    else:
                        i += 1

        clear_in_loop(self.__all_handlers)
        clear_in_loop(self.__all_handlers_before)
        clear_in_loop(self.__all_handlers_after)

    def handler(self, name: str, default_value: int, args, kwargs):
        def loop(iterator, force_wait = True):
            for func, thread, wait_result, result_without_waiting in iterator:
                if isinstance(thread, EventLeadedThread):
                    if wait_result or force_wait:
                        self.result_wait_event.clear()
                        thread.put_func(self.result_wait_event, func, args, kwargs)
                        self.result_wait_event.wait()
                        answer = thread.get_result()
                    else:
                        thread.put_func(None, func, args, kwargs)
                        answer = result_without_waiting
                else:
                    answer = func(*args, **kwargs)
                if (answer != None) and (answer != default_value):
                    return answer
            return default_value
                
        if name in self.__all_handlers_before:
            loop(self.__all_handlers_before[name], True)

        if not (name in self.__all_handlers):
            answer = default_value
        else:
            answer = loop(self.__all_handlers[name])

        if name in self.__all_handlers_after:
            loop(self.__all_handlers_after[name])

        return answer

global_event_manager = EventManager()
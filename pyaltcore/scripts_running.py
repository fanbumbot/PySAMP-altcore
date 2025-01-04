import threading
from .events import raw_event, global_event_manager, EventLeadedThread

class Script:
    def __init__(self, name: str, code: str, global_scope: dict = {}, path: str = None):
        self.name = name
        self.code = code
        self.global_scope = global_scope.copy()
        self.path = path
        self.is_first_run = True
        self.thread = EventLeadedThread(daemon=True)
        self.thread.put_code(self.code, self.global_scope)
        self.all_lock = threading.RLock()

    def disconnect(self):
        with self.all_lock:
            self.thread.destroy()
            global_event_manager.clear_subscribes_by_thread(self.thread)

    def run(self):
        with self.all_lock:
            if self.is_first_run:
                self.thread.start()
                self.is_first_run = False
            else:
                self.thread.start()

    def stop(self):
        with self.all_lock:
            self.thread.stop()

class ScriptManager:
    def __init__(self):
        self.all_scripts: dict[str, Script] = dict()
        self.is_running = False
        self.all_lock = threading.RLock()

    def is_connected(self, name: str):
        with self.all_lock:
            return name in self.all_scripts

    def run(self):
        with self.all_lock:
            self.is_running = True
            for key in self.all_scripts:
                self.all_scripts[key].run()

    def stop(self):
        with self.all_lock:
            for key in self.all_scripts:
                self.all_scripts[key].stop()
            self.is_running = False

    def connect(self, name: str, code: str,
                global_scope: dict = {}, path: str = None) -> Script:
        with self.all_lock:
            if self.is_connected(name):
                self.disconnect(name)
            self.all_scripts[name] = Script(name, code, global_scope, path)
        return self.all_scripts[name]

    def connect_by_file(self, path: str, global_scope: dict = {}) -> Script:
        with self.all_lock:
            with open(path, 'r', encoding='utf-8') as file:
                code = file.read()

            mark = path.rfind('/')
            if mark != -1:
                name = path[mark+1:]
            else:
                name = path
            if name[-3:] == ".py":
                name = name[:-3]
            script = global_script_manager.connect(name, code, global_scope, path)
        return script

    def reconnect(self, name: str, global_scope: dict = None):
        with self.all_lock:
            if self.is_connected(name):
                script = self.all_scripts[name]
                path = script.path
                if path != None:
                    if global_scope == None:
                        global_scope = script.global_scope
                    self.disconnect(name)
                    self.connect_by_file(path, global_scope)
                else:
                    name, code, global_scope = script.name, script.code, script.global_scope
                    self.connect(name, code, global_scope)
                self.all_scripts[name].run()
        return self.all_scripts[name]

    def disconnect(self, name: str):
        with self.all_lock:
            if self.is_connected(name):
                self.all_scripts[name].disconnect()
                del self.all_scripts[name]

global_script_manager = ScriptManager()


    
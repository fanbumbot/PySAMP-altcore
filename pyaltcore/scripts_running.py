import threading
from .events import RawEvent, globalEventManager, EventLeadedThread

#for comfort view in other scripts
if None is not None:
    this_script_event = None

def Stop():
    pass

@RawEvent("OnGameModeInit")
def OnInit():
    pass

class Script:
    def __init__(self, name: str, code: str, globalScope: dict = {}, path: str = None):
        self.name = name
        self.code = code
        self.globalScope = globalScope.copy()
        self.path = path
        self.is_first_run = True
        self.stopEvent = threading.Event()
        self.globalScope["this_script_event"] = self.stopEvent
        self.thread = EventLeadedThread(daemon=True)
        self.thread.PutCode(self.code, self.globalScope)
        self.allLock = threading.RLock()

    def Disconnect(self):
        with self.allLock:
            self.thread.Destroy()
            globalEventManager.ClearSubscribesByThread(self.thread)

    def Run(self):
        with self.allLock:
            if self.is_first_run:
                self.thread.start()
                self.is_first_run = False
            else:
                self.thread.Start()

    def Stop(self):
        with self.allLock:
            self.thread.Stop()

class ScriptManager:
    def __init__(self):
        self.all_scripts: dict[str, Script] = dict()
        self.is_running = False
        self.allLock = threading.RLock()

    def IsConnected(self, name: str):
        with self.allLock:
            return name in self.all_scripts

    def Run(self):
        with self.allLock:
            self.is_running = True
            for key in self.all_scripts:
                self.all_scripts[key].Run()

    def Stop(self):
        with self.allLock:
            for key in self.all_scripts:
                self.all_scripts[key].Stop()
            self.is_running = False

    def Connect(self, name: str, code: str,
                globalScope: dict = {}, path: str = None) -> Script:
        with self.allLock:
            if self.IsConnected(name):
                self.Disconnect(name)
            self.all_scripts[name] = Script(name, code, globalScope, path)
        return self.all_scripts[name]

    def ConnectByFile(self, path: str, globalScope: dict = {}) -> Script:
        with self.allLock:
            with open(path, 'r', encoding='utf-8') as file:
                code = file.read()

            mark = path.rfind('/')
            if mark != -1:
                name = path[mark+1:]
            else:
                name = path
            if name[-3:] == ".py":
                name = name[:-3]
            script = globalScriptManager.Connect(name, code, globalScope, path)
        return script

    def Reconnect(self, name: str, globalScope: dict = None):
        with self.allLock:
            if self.IsConnected(name):
                script = self.all_scripts[name]
                path = script.path
                if path != None:
                    if globalScope == None:
                        globalScope = script.globalScope
                    self.Disconnect(name)
                    self.ConnectByFile(path, globalScope)
                else:
                    name, code, globalScope = script.name, script.code, script.globalScope
                    self.Connect(name, code, globalScope)
                self.all_scripts[name].Run()
        return self.all_scripts[name]

    def Disconnect(self, name: str):
        with self.allLock:
            if self.IsConnected(name):
                self.all_scripts[name].Disconnect()
                del self.all_scripts[name]

globalScriptManager = ScriptManager()


    
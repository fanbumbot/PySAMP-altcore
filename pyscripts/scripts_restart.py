from pyaltcore import *
from components import *

@raw_event("OnPlayerCommandText", True)
def on_cmd(playerid, text: str):
    params = text.split()
    if len(params) < 2 or len(params) > 2:
        return
    if params[0] != '/pyrestart':
        return
    
    name = params[1]

    try:
        if global_script_manager.is_connected(name):
            global_script_manager.reconnect(name)
        else:
            path = 'pyscripts/'+name+'.py'
            script = global_script_manager.connect_by_file(path, {"global_manager": global_manager,
                                            "global_event_manager": global_event_manager,
                                            "global_script_manager": global_script_manager})
            script.run()
    except:
        Player(playerid).send_message("Script could not load (((")

    return True
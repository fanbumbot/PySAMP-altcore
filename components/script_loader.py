from pyaltcore import *
import os

@raw_event("OnGameModeInit")
def on_init():
    script_files = os.listdir("pyscripts")
    for file_name in script_files:
        global_script_manager.connect_by_file("pyscripts/"+file_name,
                                        {"global_manager": global_manager,
                                        "global_event_manager": global_event_manager,
                                        "global_script_manager": global_script_manager})

    global_script_manager.run()
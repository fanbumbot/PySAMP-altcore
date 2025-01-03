# PySAMP altcore
## Description
PySAMP altcore (alternative core) is a trying to remake standard core (*pysamp*) and to develop new significant opportunities for creators of gamemodes and other python scripts based on PySAMP.

The main upgrade of the core is developed multithreaded events which based on linked by PySAMP plugin standard SA:MP callbacks.


# New opportunities

- **Multithreading**
- Scripts which can be restarted and can link with events
- Global components with which it is possible to have easy control over various *server-controlled entities*: players, vehicles, objects (now is realized a part of player class)
- Expanded system of events

# Structure
Directory *'pyaltcore/'* has all bases functions, classes and other necessaries features of altcore.

In directory *'components/'* you can see all components. Files main_init is needed for main script which is in directory *'python/'*.

All custom scripts are in *'pyscripts/'*.

# Fast start and testing
To start with you should install SA:MP server (common or open.mp) and PySAMP plugin. If you have difficulties with installing, you can try to install PySAMP template (https://github.com/ackut/PySAMP-Template).

Then connect to the server and try to test a couple of scripts. You will see and test:
- Notifying of connections and disconnections of other players and greeting from server by your connection **(con_discon_notifies.py)**
- Correct spawn in countryside right in center of map **(spawn.py)**
- Command of restart scripts. Write /pyrestart [name of script] in chat and given script will be restarted. Try to write **/pyrestart hello_world** **(scripts_restart.py, hello_world.py)**

### Multithreading testing
Scripts mt_test1 and mt_test2. In file **global_manager.py** remove from **MTSafeContainerByName** and **GlobalObject** inheritable class **MTSafeClass**. Start the server and you can see message ***BRUH*** which signalize that player object attribute was out of sync inside function. Return everything as it was and no one ***BRUH*** cannot be seen.
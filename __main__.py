import json
import pittsburg
import san_diego

# -- Start Game Function --
def start_game():
    with open("savegame.json", "r+") as f:
        contents = f.read().strip()
        if contents == "" or contents == "{}":
            pittsburg.run_game()
        else:
            level = json.loads(contents).get("level", 1)
            if level == 1:
                pittsburg.run_game()
            elif level == 2:
                san_diego.run_game()

start_game()

# main.py
import json
import os
import traceback
from ui.app import FrontendApp 

CONFIG_PATH = "config.json"

def load_config(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    try:
        config = load_config(CONFIG_PATH)
        app = FrontendApp(config)  
        app.run()
    except Exception as e:
        print("Fatal error starting application:", e)
        traceback.print_exc()

if __name__ == "__main__":
    main()
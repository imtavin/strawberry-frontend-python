import json
from ui.app import FrontendApp

if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)

    app = FrontendApp(config)
    app.mainloop()

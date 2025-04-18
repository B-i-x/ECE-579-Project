# main.py
from BearDownBots.gui import BearDownBotsApp
from BearDownBots.app_context import set_app

def main():
    app = BearDownBotsApp()
    set_app(app)
    app.mainloop()              

if __name__ == "__main__":
    main()

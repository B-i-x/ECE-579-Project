# __init__.py
from BearDownBots.gui import BearDownBotsApp
from BearDownBots.app_context import set_app

from BearDownBots.environment.campus import Campus

def main():
    app = BearDownBotsApp(width=1000, height=800)
    set_app(app)

    campus = Campus(rows=300, cols=350)


    app.mainloop()

if __name__ == "__main__":
    main()

# __init__.py
from BearDownBots.gui import BearDownBotsApp
from BearDownBots.app_context import set_app

from BearDownBots.environment.campus import Campus
from BearDownBots.environment.sidewalks import Sidewalks

def main():
    app = BearDownBotsApp(width=600, height=600)
    set_app(app)

    campus = Campus(rows=300, cols=300)
    sidewalks = Sidewalks(campus)
    sidewalks.draw()

    app.mainloop()

if __name__ == "__main__":
    main()

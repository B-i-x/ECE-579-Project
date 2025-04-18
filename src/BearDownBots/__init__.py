# __init__.py
from BearDownBots.gui import BearDownBotsApp
from BearDownBots.app_context import set_app

from BearDownBots.environment.campus import Campus

def main():
    app = BearDownBotsApp(width=600, height=400)
    set_app(app)

    # draw a campus of 20×30 cells of size 20px
    campus = Campus(rows=20, cols=30, cell_size=20)


    app.mainloop()

if __name__ == "__main__":
    main()

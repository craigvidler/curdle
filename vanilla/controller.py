from curdle.config import AppStatus, MenuOption


class Controller:
    def __init__(self, wordle, view):
        self.wordle = wordle
        self.view = view

    def menu(self):
        while True:
            option = self.view.menu()

            if option is MenuOption.NEW_GAME:
                self.wordle.new_game()
                break
            if option is MenuOption.STATS:
                print(self.view.stats(self.wordle.stats))
            if option is MenuOption.EXIT:
                raise SystemExit()

    def handle_input(self):
        input_ = self.view.get_input(self.wordle.turn)
        self.wordle.submit(input_)

    def run(self):
        self.wordle.new_game()

        while self.wordle.app_status is AppStatus.PLAYING:
            self.handle_input()
            if self.wordle.app_status is not AppStatus.PLAYING:
                self.menu()

from curdle.config import AppStatus, MenuOption


class Controller:
    def __init__(self, wordle, view):
        self.wordle = wordle
        self.view = view

    def handle_menu(self):
        while True:
            option = self.view.menu()

            if option is MenuOption.NEW_GAME:
                self.wordle.new_game()
                break
            if option is MenuOption.STATS:
                self.view.stats(self.wordle.stats)
            if option is MenuOption.EXIT:
                raise SystemExit()

    def handle_guess(self):
        guess = self.view.get_input(self.wordle.turn)
        self.wordle.submit(guess)

    def run(self):
        self.wordle.new_game()

        while True:
            self.handle_guess()
            if self.wordle.app_status is not AppStatus.PLAYING:
                self.handle_menu()

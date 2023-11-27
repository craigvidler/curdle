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
            # if option is MenuOption.STATS:
            #     print(self.view.stats(wordle.stats))
            if option is MenuOption.EXIT:
                raise SystemExit()

    def handle_guess(self, guess):
        self.wordle.submit(guess)

    def run(self):

        self.wordle.new_game()

        while self.wordle.app_status is AppStatus.PLAYING:
            # pass turn number and callback to view input method
            self.view.get_input(self.handle_guess, self.wordle.turn)
            if self.wordle.app_status is not AppStatus.PLAYING:
                self.menu()

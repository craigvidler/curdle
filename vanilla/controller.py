from curdle.config import AppStatus


class Controller:
    def __init__(self, wordle, view):
        self.wordle = wordle
        self.view = view

    # def reset(self):
    #     """
    #     Reset game (model/view) for initial setup + to enable multiple games.
    #     """
    #     self.wordle.new_game()

    def handle_guess(self, guess):
        self.wordle.submit(guess)

    def run(self):

        self.wordle.new_game()

        while self.wordle.app_status is AppStatus.PLAYING:
            # pass turn number and callback to view input method
            self.view.get_input(self.handle_guess, self.wordle.turn)

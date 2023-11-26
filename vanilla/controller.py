class Controller:
    def __init__(self, wordle, view):
        self.wordle = wordle
        self.view = view

    # def reset(self):
    #     """
    #     Reset game (model/view) for initial setup + to enable multiple games.
    #     """
    #     self.wordle.new_game()

    def run(self):

        self.wordle.new_game()

        while self.wordle.app_status == 'playing':
            guess = input(f'Round {self.wordle.turn}: ').lower()
            # guess = self.view.do_turn(turn)
            self.wordle.submit(guess)

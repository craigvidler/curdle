from model import Wordle  # Just for typehint below. Good practice?


class Controller:
    def __init__(self, view, wordle: Wordle):
        """Instantiate controller, set up view and model."""

        self.wordle = wordle
        self.view = view

    def menu(self):
        """Display menu and handle choices."""

        option = self.view.menu()

        if option == 'quit':
            raise SystemExit()
        elif option == 'new_game':
            self.reset()

    def reset(self):
        """
        Reset game (model/view) for initial setup + to enable multiple games.
        """
        self.wordle.new_game()
        self.view.reset()

    def run(self):
        """Run the application main loop."""

        self.reset()

        # MAIN LOOP
        while self.wordle.state == 'playing':
            # get the turn number before it's incremented by a valid guess
            turn = self.wordle.turn

            # `guess` will be a completed row (5 letters)
            guess = self.view.do_turn(turn)
            scored_guess, response = self.wordle.submit(guess)

            if scored_guess:  # if guess found in list
                self.view.draw_scored_guess(scored_guess, turn)
            else:
                self.view.announce(response)  # ie 'not in word list' error

            self.view.draw_tracker(self.wordle.tracker)

            # output message if solved or game over, enable menu
            if self.wordle.state != 'playing':
                self.view.announce(response, end_game=True)
                self.menu()

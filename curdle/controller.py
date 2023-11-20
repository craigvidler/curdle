from .model import Wordle  # Just for typehint below. Good practice?
from .view import MenuOption  # Good practice?


class Controller:
    def __init__(self, view, wordle: Wordle):
        """Instantiate controller, set up view and model."""

        self.wordle = wordle
        self.view = view

    def menu(self, end_game=False):
        """Display menu and handle choices."""

        selected = self.view.menu(end_game=end_game)  # flag disables 0 to close menu

        if selected == MenuOption.NEW_GAME:
            self.reset()
        elif selected == MenuOption.EXIT:
            raise SystemExit()

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

            # (used to read: `guess` will be a completed row (5 letters))
            # FIXME: this doesn't feel right to take menu input over a channel
            # designed for gameplay stuff, and also duplicating menu() above.
            user_input = self.view.do_turn(turn)

            if isinstance(user_input, MenuOption):
                if user_input == MenuOption.NEW_GAME:
                    self.reset()
                if user_input == MenuOption.EXIT:
                    raise SystemExit()
                continue

            scored_guess, response = self.wordle.submit(user_input)

            if scored_guess:  # if guess found in list
                self.view.draw_scored_guess(scored_guess, turn)
            else:
                self.view.alert(response)  # ie 'not in word list' error

            self.view.draw_tracker(self.wordle.tracker)

            # output message if solved or game over, enable menu
            if self.wordle.state != 'playing':
                self.view.alert(response, end_game=True)  # flag joins threads
                self.menu(end_game=True)  # flag disables 0 to close menu

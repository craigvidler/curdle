import curses
import sys
from wordle import Wordle
from view import View


class Curdle:
    def __init__(self, view, wordle):
        self.wordle = wordle
        self.view = view

    def menu(self):
        self.view.popup('[N]ew game | [Q]uit', duration=0)
        option = self.view.menu()
        if option == 'q':
            raise SystemExit()
        elif option == 'n':
            self.reset()

    def reset(self):
        self.wordle.new_game()
        self.view.reset()

    def run(self):
        self.reset()

        # MAIN LOOP
        while self.wordle.state == 'playing':
            # get the turn number before it's incremented by a valid guess
            turn = self.wordle.turn

            # `guess` will be a completed row (5 letters)
            guess = self.view.do_turn(turn)
            scored_guess, response = self.wordle.submit(guess)

            if scored_guess:  # if guess found in list
                self.view.guess = ''  # reset guess buffer for next turn
                self.view.draw_scored_guess(scored_guess, turn)
            else:
                self.view.popup(response)  # 'not in word list' error

            self.view.draw_tracker(self.wordle.tracker)

            # output message if solved or game over, enable menu
            if self.wordle.state != 'playing':
                self.view.popup(response)
                self.view.timer.join()  # will block till popup clears
                self.menu()


def main(stdscr):
    # Pass in answer if required during dev
    answer = sys.argv[1] if len(sys.argv) > 1 else ''
    wordle = Wordle(answer)  # game object/model
    view = View(curses, stdscr)
    Curdle(view, wordle).run()


curses.wrapper(main)

import curses
from string import ascii_letters
import sys
from wordle import Wordle
from view import Color, View


class Curdle:
    def __init__(self, view, wordle):
        self.wordle = wordle
        self.view = view

    def do_round(self, guess):

        # loop while in row until a valid guess is entered
        # FIXME: mess-but-works prototype standard, clean up

        while True:
            length = len(guess)

            # Get input key. try/except here because window resize will crash
            # getkey() without it.
            try:
                key = self.view.guesseswin.getkey()
            except curses.error:
                pass

            # if valid letter, display it in white box
            if key in ascii_letters and length < 5:
                guess += key.lower()
                letter = f' {key.upper()} '
                self.view.guesseswin.addstr((self.wordle.round - 1) * 2, length * 4, letter, Color.BL_WHITE)

            # if BACKSPACE (KEY_BACKSPACE Win/Lin; `\x7F` Mac; '\b' just in case)
            elif key in ('KEY_BACKSPACE', '\x7F', '\b') and guess:
                guess = guess[:-1]
                self.view.guesseswin.addstr((self.wordle.round - 1) * 2, (length - 1) * 4, '   ', Color.BL_WHITE)

            # if ENTER (should work cross-platform)
            elif key in ('\n', '\r'):
                scored_guess, response = self.wordle.submit(guess)
                return scored_guess, response, guess

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
        guess = ''
        while self.wordle.state == 'playing':
            # get the round number before it's incremented by a valid guess
            game_round = self.wordle.round
            scored_guess, response, guess = self.do_round(guess)
            if scored_guess:
                guess = ''
                self.view.draw_scored_guess(scored_guess, game_round)
            else:
                self.view.popup(response)

            self.view.draw_tracker(self.wordle.letter_tracker)

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

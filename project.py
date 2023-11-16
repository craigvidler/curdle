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
        while True:
            key = self.view.guesseswin.getkey()
            if key == 'q':
                raise SystemExit()
            elif key == 'n':
                self.reset()
                break

    def reset(self):
        self.wordle.new_game()
        curses.flushinp()  # prevent input buffer dumping into new game
        self.view.draw_title()
        self.view.draw_guesses()
        self.view.popup()  # without args will clear popup window
        self.view.draw_tracker()

    def run(self):
        curses.use_default_colors()  # is this necessary?
        curses.curs_set(False)  # no cursor
        Color.setup(curses)
        self.reset()

        # MAIN LOOP
        guess = ''
        while self.wordle.state == 'playing':
            scored_guess, response, guess = self.do_round(guess)
            if scored_guess:
                guess = ''
                for i, (letter, score) in enumerate(scored_guess):
                    letter = f' {letter.upper()} '
                    self.view.guesseswin.addstr((self.wordle.round - 2) * 2, i * 4, letter, Color.letter_colors[score])
            else:
                self.view.popup(response)

            self.view.draw_tracker(self.wordle.letter_tracker)
            self.view.guesseswin.refresh()

            # output message if solved or game over, enable menu
            if self.wordle.state != 'playing':
                self.view.popup(response)
                self.view.timer.join()  # will block till popup clears
                self.menu()


def main(stdscr):
    # Pass in answer if required during dev
    answer = sys.argv[1] if len(sys.argv) > 1 else ''
    wordle = Wordle(answer)  # game object/model
    view = View(curses, stdscr)  # view
    Curdle(view, wordle).run()


curses.wrapper(main)

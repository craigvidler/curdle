import curses
from string import ascii_letters
import sys
from wordle import Wordle
from view import Color, View


class Curdle:
    def __init__(self, stdscr, view, wordle):
        self.wordle = wordle
        self.view = view
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()

        # windows
        self.title = curses.newwin(1, self.width + 1, 0, 0)  # needs + 1 to fill width?!
        self.guesses = curses.newwin(12, 19, 5, self.width // 2 - 9)
        self.letter_tracker = curses.newwin(5, 39, 19, self.width // 2 - 19)

    def draw_title(self):
        title = 'curdle'
        self.title.addstr(0, 0, ' ' * (self.width), Color.WH_DGREY)
        self.title.addstr(0, self.width // 2 - len(title) // 2, title, Color.WH_DGREY)

        menu = '<esc> for menu'
        self.title.addstr(0, self.width - len(menu) - 1, '<esc>', Color.WH_DGREY)
        self.title.addstr(' for menu', Color.LG_DGREY)
        self.title.refresh()

    def draw_guesses(self):

        for i in range(6):
            y = i * 2
            for j in range(5):
                self.guesses.addstr(y, j * 4, '   ', Color.BL_WHITE)
        self.guesses.refresh()

    def draw_tracker(self, tracker=None):

        letters = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
        x = 0

        for i, row in enumerate(letters):
            y = i * 2
            if i == 1:
                x += 2
            if i == 2:
                x += 4
            for j, letter in enumerate(row):
                color = Color.BL_LGREY if not tracker else Color.letter_colors[tracker[letter]]
                self.letter_tracker.addstr(y, x + j * 4, f' {letter.upper()} ', color)

        self.letter_tracker.refresh()

    def do_round(self, guess):

        # loop while in row until a valid guess is entered
        # FIXME: mess-but-works prototype standard, clean up

        while True:
            length = len(guess)

            # Get input key. try/except here because window resize will crash
            # getkey() without it.
            try:
                key = self.guesses.getkey()
            except curses.error:
                pass

            # if valid letter, display it in white box
            if key in ascii_letters and length < 5:
                guess += key.lower()
                letter = f' {key.upper()} '
                self.guesses.addstr((self.wordle.round - 1) * 2, length * 4, letter, Color.BL_WHITE)

            # if BACKSPACE (KEY_BACKSPACE Win/Lin; `\x7F` Mac; '\b' just in case)
            elif key in ('KEY_BACKSPACE', '\x7F', '\b') and guess:
                guess = guess[:-1]
                self.guesses.addstr((self.wordle.round - 1) * 2, (length - 1) * 4, '   ', Color.BL_WHITE)

            # if ENTER (should work cross-platform)
            elif key in ('\n', '\r'):
                scored_guess, response = self.wordle.submit(guess)
                return scored_guess, response, guess

    def menu(self):
        self.view.popup('[N]ew game | [Q]uit', duration=0)
        while True:
            key = self.guesses.getkey()
            if key == 'q':
                raise SystemExit()
            elif key == 'n':
                self.reset()
                break

    def reset(self):
        self.wordle.new_game()
        curses.flushinp()  # prevent input buffer dumping into new game
        self.draw_title()
        self.draw_guesses()
        self.view.popup()  # no message will clear popup window
        self.draw_tracker()

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
                    self.guesses.addstr((self.wordle.round - 2) * 2, i * 4, letter, Color.letter_colors[score])
            else:
                self.view.popup(response)

            self.draw_tracker(self.wordle.letter_tracker)
            self.guesses.refresh()

            # output message if solved or game over, enable menu
            if self.wordle.state != 'playing':
                self.view.popup(response)
                self.view.timer.join()  # will block till popup clears
                self.menu()


def main(stdscr):
    # Pass in answer if required during dev
    answer = sys.argv[1] if len(sys.argv) > 1 else ''
    wordle = Wordle(answer)  # Game object
    view = View(curses, stdscr)
    Curdle(stdscr, view, wordle).run()


curses.wrapper(main)

import curses
from string import ascii_letters
import sys
from threading import Timer
from wordle import Wordle
from enum import IntEnum


class Color:
    """
    Set up curses color pairs in a global Color object with dot syntax.
    Since colors can't be set up till after curses is loaded, using a global
    enum as we'd like isn't simple. This is close and less faff.

    Example: 'BL_WHITE': (1, 234, 255) ->
    curses.init_pair(1, 234, 255)
    Color.BL_WHITE = curses.color_pair(1) | curses.A_BOLD
    """

    @classmethod
    def setup(cls):
        """Create color pairs and class attributes from colors dict."""

        colors = {
            # name: (color pair id, text color, background color)
            'BL_WHITE': (1, 234, 255),  # blackish on white
            'BL_LGREY': (2, 234, 250),  # blackish on light grey
            'WH_DGREY': (3, 255, 239),  # white on dark grey
            'WH_YELLOW': (4, 255, 136),  # white on yellow
            'WH_GREEN': (5, 255, 28),  # white on green
            'LG_DGREY': (6, 250, 239)  # light grey on dark grey
        }

        for name, (pair_id, text_color, bg_color) in colors.items():
            curses.init_pair(pair_id, text_color, bg_color)
            setattr(cls, name, curses.color_pair(pair_id) | curses.A_BOLD)

        cls.letter_colors = (
            cls.BL_LGREY, cls.WH_DGREY, cls.WH_YELLOW, cls.WH_GREEN
        )


class Curdle:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.guess_x = None
        self.timer = None
        self.popup = curses.newwin(1, 21, 17, curses.COLS // 2 - 10)

    def draw_title_bar(self):
        addstr = self.stdscr.addstr
        title = 'curdle'
        addstr(0, 0, ' ' * curses.COLS, Color.WH_DGREY)
        addstr(0, curses.COLS // 2 - len(title) // 2, title, Color.WH_DGREY)

        menu = '<esc> for menu'
        addstr(0, curses.COLS - len(menu) - 1, '<esc>', Color.WH_DGREY)
        addstr(' for menu', Color.LG_DGREY)

    def draw_guesses_board(self):
        guess_width = 19
        self.guess_x = curses.COLS // 2 - guess_width // 2

        for i in range(6):
            y = 5 + i * 2
            for j in range(5):
                self.stdscr.addstr(y, self.guess_x + j * 4, '   ', Color.BL_WHITE)

    def show_popup(self, message, duration=2.5):

        self.popup.clear()
        self.popup.addstr(0, 21 // 2 - len(message) // 2, message)
        self.popup.refresh()

        if not duration:
            return

        if self.timer:
            self.timer.cancel()
        self.timer = Timer(duration, self.clear_popup)
        self.timer.start()

    def clear_popup(self):
        self.popup.clear()
        self.popup.refresh()

    def draw_tracker(self, tracker=None):

        center_x = curses.COLS // 2
        tracker_width = 39
        tracker_x = center_x - tracker_width // 2

        letters = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']

        for i, row in enumerate(letters):
            y = 19 + i * 2
            if i == 1:
                tracker_x += 2
            if i == 2:
                tracker_x += 4
            for j, letter in enumerate(row):
                color = Color.BL_LGREY if not tracker else Color.letter_colors[tracker[letter]]
                self.stdscr.addstr(y, tracker_x + j * 4, f' {letter.upper()} ', color)

    def do_round(self, guess):

        # loop while in row until a valid guess is entered
        # FIXME: mess-but-works prototype standard, clean up

        while True:
            length = len(guess)

            # Get input key. try/except here because window resize will crash
            # getkey() without it.
            try:
                key = self.stdscr.getkey()
            except curses.error:
                pass

            # if valid letter, display it in white box
            if key in ascii_letters and length < 5:
                guess += key.lower()
                letter = f' {key.upper()} '
                self.stdscr.addstr(5 + (wordle.round - 1) * 2, self.guess_x + length * 4, letter, Color.BL_WHITE)

            # if BACKSPACE (KEY_BACKSPACE Win/Lin; `\x7F` Mac; '\b' just in case)
            elif key in ('KEY_BACKSPACE', '\x7F', '\b') and guess:
                guess = guess[:-1]
                self.stdscr.addstr(5 + (wordle.round - 1) * 2, self.guess_x + (length - 1) * 4, '   ', Color.BL_WHITE)

            # if ENTER (should work cross-platform)
            elif key in ('\n', '\r'):
                scored_guess, response = wordle.submit(guess)
                return scored_guess, response, guess

    def menu(self):
        self.show_popup('[N]ew game | [Q]uit', duration=0)
        while True:
            key = self.stdscr.getkey()
            if key == 'q':
                raise SystemExit()
            elif key == 'n':
                self.reset()
                break

    def reset(self):
        wordle.new_game()
        curses.flushinp()  # prevent input buffer dumping into new game
        self.draw_title_bar()
        self.draw_guesses_board()
        self.clear_popup()
        self.draw_tracker()

    def run(self):
        curses.use_default_colors()  # is this necessary?
        curses.curs_set(False)  # no cursor

        Color.setup()
        self.reset()

        # MAIN LOOP
        guess = ''
        while wordle.state == 'playing':
            scored_guess, response, guess = self.do_round(guess)
            if scored_guess:
                guess = ''
                for i, (letter, score) in enumerate(scored_guess):
                    letter = f' {letter.upper()} '
                    self.stdscr.addstr(5 + (wordle.round - 2) * 2, self.guess_x + i * 4, letter, Color.letter_colors[score])
            else:
                self.show_popup(response)

            self.draw_tracker(wordle.letter_tracker)
            self.stdscr.refresh()

            # output message if solved or game over, enable menu
            if wordle.state != 'playing':
                self.show_popup(response)
                self.timer.join()  # will block till popup clears
                self.menu()


def main(stdscr):
    Curdle(stdscr).run()


# Game object. Pass in answer if required during dev
answer = sys.argv[1] if len(sys.argv) > 1 else ''
wordle = Wordle(answer)

curses.wrapper(main)

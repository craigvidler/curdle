from curses import panel
from enum import Enum
from string import ascii_letters
from threading import Timer


class Color:
    """
    Set up curses color pairs in a global Color object with dot syntax. Since
    colors can't be set up till after curses is loaded, using a simple global
    enum as we'd like isn't easy. This is close and less faff.

    Example: 'BL_WHITE': (1, 234, 255) ->
    curses.init_pair(1, 234, 255)
    Color.BL_WHITE = curses.color_pair(1) | curses.A_BOLD
    """

    @classmethod
    def setup(cls, curses):
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


class MenuOption(str, Enum):
    NEW_GAME = 'new_game'
    QUIT = 'quit'


class View:

    def __init__(self, curses, stdscr):

        self.curses = curses
        self.stdscr = stdscr
        self.timer = None
        self.height, self.width = stdscr.getmaxyx()
        self.guess = ''  # buffer holding guess-in-progress

        # windows and panels (improve magic numbers? shorten lines?)
        middle_x = self.width // 2
        self.titlewin, self.titlepanel = self.create_panels(1, self.width + 1, 0, 0)  # needs + 1 to fill width?!
        self.guesseswin, self.guessespanel = self.create_panels(12, 19, 5, middle_x - 9)
        self.alertwin, self.alertpanel = self.create_panels(1, 21, 17, middle_x - 10)
        self.trackerwin, self.trackerpanel = self.create_panels(5, 39, 19, middle_x - 19)
        self.menuwin, self.menupanel = self.create_panels(13, 28, 8, middle_x - 14)

        self.setup_curses()

    def setup_curses(self):
        self.curses.use_default_colors()  # is this necessary?
        self.curses.curs_set(False)  # no cursor
        Color.setup(self.curses)

    def create_panels(self, h, w, y, x):
        new_window = self.curses.newwin(h, w, y, x)
        new_panel = panel.new_panel(new_window)
        return new_window, new_panel

    def draw_title(self):
        # FIXME: title and menu prompt should be moved from view.py and passed in
        title = 'curdle'
        win = self.titlewin
        win.addstr(0, 0, ' ' * (self.width), Color.WH_DGREY)
        win.addstr(0, self.width // 2 - len(title) // 2, title, Color.WH_DGREY)

        menu = 'press 0 for menu'  # FIXME: hack
        win.addstr(0, self.width - len(menu) - 1, 'press ', Color.LG_DGREY)
        win.addstr('0', Color.WH_DGREY)
        win.addstr(' for menu', Color.LG_DGREY)
        win.refresh()

    def draw_guesses(self):

        # stdscr doesn't need this but windows taking input do, otherwise
        # eg arrow keys will be read as ABCD (ie valid input letters).
        self.guesseswin.keypad(True)

        for i in range(6):
            y = i * 2
            for j in range(5):
                self.guesseswin.addstr(y, j * 4, '   ', Color.BL_WHITE)
        self.guesseswin.refresh()

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
                self.trackerwin.addstr(y, x + j * 4, f' {letter.upper()} ', color)

        self.trackerwin.refresh()

    def draw_menu(self):
        self.menuwin.border()
        self.hide_menu()

    def alert(self, message='', duration=2.5, end_game=False):
        """
        Show a message, either for `duration` or indefinitely if `duration` is
        0. If called without arguments, clear the alert window. Only set a
        timer if both `duration` and `message` given. If game finished, join
        threads to a) block menu prompt appearing till after current message
        duration; b) close threads gracefully to avoid eg app restarting
        after ctrl-C exit during end game message.
        """

        self.alertwin.clear()
        if message:
            self.alertwin.addstr(0, 21 // 2 - len(message) // 2, message)
        self.alertwin.refresh()

        if not duration or not message:
            return

        if self.timer:
            self.timer.cancel()
        self.timer = Timer(duration, self.alert)
        self.timer.start()

        if end_game:
            self.timer.join()

    def reset(self):
        self.draw_title()
        self.draw_guesses()
        self.alert()  # without args will clear alert window
        self.draw_tracker()
        self.draw_menu()

    def draw_scored_guess(self, scored_guess, turn):
        for i, (letter, score) in enumerate(scored_guess):
            letter = f' {letter.upper()} '
            self.guesseswin.addstr((turn - 1) * 2, i * 4, letter, Color.letter_colors[score])
        self.guesseswin.refresh()

        # a scored guess means turn is over, reset guess buffer for next turn
        self.guess = ''

    def menu(self):
        # discard any input buffered during end game message
        self.curses.flushinp()
        self.show_menu()

        while True:
            # temporary: key-based menu will be replaced soon
            key = self.guesseswin.getkey()
            if key == 'q':
                return MenuOption.QUIT
            elif key == 'n':
                self.hide_menu()
                return MenuOption.NEW_GAME
            elif key == 'x':
                self.hide_menu()
                break

    def show_menu(self):
        self.menupanel.show()
        panel.update_panels()
        self.stdscr.refresh()

    def hide_menu(self):
        # .hide() throws error if panel is not visible
        if not self.menupanel.hidden():
            self.menupanel.hide()
            panel.update_panels()
            self.stdscr.refresh()

    def do_turn(self, turn):

        # loop while in row until a valid guess is entered
        while True:
            length = len(self.guess)

            # Get input key. try/except here because window resize will crash
            # getkey() without it.
            try:
                key = self.guesseswin.getkey()
            except self.curses.error:
                pass

            # if valid letter, display it in white box
            if key in ascii_letters and length < 5:
                self.guess += key.lower()
                letter = f' {key.upper()} '
                self.guesseswin.addstr((turn - 1) * 2, length * 4, letter, Color.BL_WHITE)

            # if BACKSPACE (KEY_BACKSPACE Win/Lin; `\x7F` Mac; '\b' just in case)
            elif key in ('KEY_BACKSPACE', '\x7F', '\b') and self.guess:
                self.guess = self.guess[:-1]
                self.guesseswin.addstr((turn - 1) * 2, (length - 1) * 4, '   ', Color.BL_WHITE)

            # if ENTER (should work cross-platform)
            elif key in ('\n', '\r'):
                if length == 5:
                    return self.guess
                self.alert('Not enough letters')  # FIXME: hardcoded message

            # display menu
            elif key == '0':
                self.menu()

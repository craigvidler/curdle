from curses import panel
from enum import IntEnum, auto
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
            'LG_DGREY': (6, 250, 239),  # light grey on dark grey
            'WH_DRED_NORMAL': (8, 255, 88),  # white on dark red (not bold)
            'WH_RED': (7, 255, 124)  # white on red
        }

        for name, (pair_id, text_color, bg_color) in colors.items():
            curses.init_pair(pair_id, text_color, bg_color)
            # no better way?
            if name == 'WH_DRED_NORMAL':
                setattr(cls, name, curses.color_pair(pair_id))
            else:
                setattr(cls, name, curses.color_pair(pair_id) | curses.A_BOLD)

        cls.letter_colors = (
            cls.BL_LGREY, cls.WH_DGREY, cls.WH_YELLOW, cls.WH_GREEN
        )


class MenuOption(IntEnum):
    """Menu options. Provide int or string based on name as needed."""
    NEW_GAME = auto()
    STATS = auto()
    EXIT = auto()

    def __str__(self):
        return self.name.replace('_', ' ')


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
        self.menuwin, self.menupanel = self.create_panels(7, 17, 6, middle_x - 8)

        self.menu_selected = MenuOption(1)  # default to first item

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

        prompt = ' menu on/off: press  0 '
        win.addstr(0, self.width - len(prompt), prompt[:-3], Color.WH_DRED_NORMAL)
        win.addstr(prompt[-3:], Color.WH_RED)
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

    def setup_menu(self):
        self.menuwin.keypad(True)  # to handle arrow key input properly
        self.menuwin.border()
        self.hide_menu()  # hidden by default

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
        self.setup_menu()
        self.guess = ''
        self.menu_selected = MenuOption(1)

    def draw_scored_guess(self, scored_guess, turn):
        for i, (letter, score) in enumerate(scored_guess):
            letter = f' {letter.upper()} '
            self.guesseswin.addstr((turn - 1) * 2, i * 4, letter, Color.letter_colors[score])
        self.guesseswin.refresh()

        # a scored guess means turn is over, reset guess buffer for next turn
        self.guess = ''

    def get_key(self, window):
        # Get input key. try/except or terminal window resize will crash getkey().
        try:
            return window.getkey()
        except self.curses.error:
            pass

    def menu(self, end_game=False):
        # discard any input buffered during end game message
        self.curses.flushinp()
        self.show_menu()

        while True:

            # get user input keypress
            key = self.get_key(self.menuwin)

            # change selected option with up/down, limited to options available
            if key == 'KEY_UP' and self.menu_selected > MenuOption(1):
                self.menu_selected = MenuOption(self.menu_selected - 1)
            elif key == 'KEY_DOWN' and self.menu_selected < len(MenuOption):
                self.menu_selected = MenuOption(self.menu_selected + 1)

            # Selected option entered, return it to controller.
            elif key in ('\n', '\r'):
                #  FIXME: temporary safeguard while STATS unavailable
                if self.menu_selected != MenuOption.STATS:
                    return self.menu_selected

            # close menu, but disabled for end game menu
            elif key == '0' and not end_game:
                self.hide_menu()
                break

            self.show_menu()

    def show_menu(self):
        def center_print(win, text, y, attrs):
            _, width = win.getmaxyx()
            x = width // 2 - len(text) // 2
            win.addstr(y, x, text, attrs)

        margin_top = 1

        for option in MenuOption:
            if option == self.menu_selected:
                attrs = self.curses.A_REVERSE
            else:
                attrs = self.curses.A_NORMAL

            center_print(self.menuwin, f' {option} ', margin_top + option, attrs)

        self.menuwin.refresh()

        if self.menupanel.hidden():
            self.menupanel.show()
            panel.update_panels()
            self.stdscr.refresh()

    def hide_menu(self):
        # .hide() throws error if panel is already hidden
        if not self.menupanel.hidden():
            self.menupanel.hide()
            panel.update_panels()
            self.stdscr.refresh()

    def do_turn(self, turn):

        # loop while in row until a valid guess is entered
        while True:
            length = len(self.guess)

            # get user input keypress
            key = self.get_key(self.guesseswin)

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

            # Display menu. Return if there's something to give controller,
            # otherwise (ie '0' pressed to close menu), stay in loop.
            elif key == '0':
                selected = self.menu()
                if selected:
                    return selected

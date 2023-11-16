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


class View:

    def __init__(self, curses, stdscr):
        self.timer = None
        self.height, self.width = stdscr.getmaxyx()

        # windows
        # improve magic numbers?
        self.popupwin = curses.newwin(1, 21, 17, self.width // 2 - 10)
        self.titlewin = curses.newwin(1, self.width + 1, 0, 0)  # needs + 1 to fill width?!
        self.guesseswin = curses.newwin(12, 19, 5, self.width // 2 - 9)
        self.trackerwin = curses.newwin(5, 39, 19, self.width // 2 - 19)

    def draw_title(self):
        # title and menu prompt should be moved from view.py and passed in
        title = 'curdle'
        win = self.titlewin
        win.addstr(0, 0, ' ' * (self.width), Color.WH_DGREY)
        win.addstr(0, self.width // 2 - len(title) // 2, title, Color.WH_DGREY)

        menu = '<esc> for menu'
        win.addstr(0, self.width - len(menu) - 1, '<esc>', Color.WH_DGREY)
        win.addstr(' for menu', Color.LG_DGREY)
        win.refresh()

    def draw_guesses(self):

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

    def popup(self, message='', duration=2.5):
        """
        Show a popup message, either for `duration` or indefinitely if
        `duration` is 0. If called without arguments, clear the popup
        window. Only set a timer if both `duration` and `message` given.
        """

        self.popupwin.clear()
        if message:
            self.popupwin.addstr(0, 21 // 2 - len(message) // 2, message)
        self.popupwin.refresh()

        if not duration or not message:
            return

        if self.timer:
            self.timer.cancel()
        self.timer = Timer(duration, self.popup)
        self.timer.start()

import curses
from string import ascii_letters
import sys
from threading import Timer
from wordle import Wordle

# Game object. Pass in answer if required during dev
answer = sys.argv[1] if len(sys.argv) > 1 else ''
wordle = Wordle(answer)
wordle.new_game()


class Color():
    # Can't create colors till after curses initialised by main wrapper,
    # making them difficult to define as global constants as I'd like; this
    # is an alternative. Enum hard to work with here so just raw class.
    # Actual colors set in setup_colors().
    pass


def setup_curses():
    curses.use_default_colors()  # is this necessary?
    curses.curs_set(False)  # no cursor


def setup_colors():
    color_pairs = {
        'BL_WHITE': (234, 255),  # blackish on white
        'BL_LGREY': (234, 250),  # blackish on light grey
        'WH_DGREY': (255, 239),  # white on dark grey
        'WH_YELLOW': (255, 136),  # white on yellow
        'WH_GREEN': (255, 28),  # white on green
        'LG_DGREY': (250, 239)  # light grey on dark grey
    }

    # Example: 'BL_WHITE': (234, 255) ->
    # curses.init_pair(1, 234, 255)
    # Color.BL_WHITE = curses.color_pair(1) | curses.A_BOLD
    i = 1  # next line too ugly using enumerate
    for name, (fg_color, bg_color) in color_pairs.items():
        curses.init_pair(i, fg_color, bg_color)
        setattr(Color, name, curses.color_pair(i) | curses.A_BOLD)
        i += 1


def clear_popup(window):
    window.clear()
    window.refresh()


def popup(window, timer, message):
    offset = 21 // 2 - len(message) // 2

    if timer:
        timer.cancel()

    window.clear()
    window.addstr(0, offset, message)
    window.refresh()

    timer = Timer(2, clear_popup, args=(window,))
    timer.start()
    return timer


def draw_tracker(stdscr, tracker=None):
    colors = (Color.BL_LGREY, Color.WH_DGREY, Color.WH_YELLOW, Color.WH_GREEN)

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
            # if tracker:
            #     print(tracker[letter])
            color = Color.BL_LGREY if not tracker else colors[tracker[letter]]
            stdscr.addstr(y, tracker_x + j * 4, f' {letter.upper()} ', color)

    stdscr.refresh()


def main(stdscr):
    setup_curses()
    setup_colors()

    # set up x-centering
    center_x = curses.COLS // 2
    guess_width = 19
    guess_x = center_x - guess_width // 2

    colors = (Color.BL_LGREY, Color.WH_DGREY, Color.WH_YELLOW, Color.WH_GREEN)

    # title bar
    title = 'curdle'
    stdscr.addstr(0, 0, ' ' * curses.COLS, Color.WH_DGREY)
    stdscr.addstr(0, center_x - len(title) // 2, title, Color.WH_DGREY)

    # menu. FIXME FFS
    menu = '<esc> for menu'
    stdscr.addstr(0, curses.COLS - len(menu) - 1, '', Color.WH_DGREY)

    for item in menu.split(' '):
        if item == '<esc>':
            stdscr.addstr(item, Color.WH_DGREY)
        else:
            stdscr.addstr(' ' + item, Color.LG_DGREY)

    # set up guesses board
    for i in range(6):
        y = 5 + i * 2
        for j in range(5):
            stdscr.addstr(y, guess_x + j * 4, '   ', Color.BL_WHITE)

    # create new window for response output and timer that controls it
    popup_window = curses.newwin(1, 21, 17, center_x - 10)
    timer = None

    # set up letter tracker
    draw_tracker(stdscr)

    # for each row in guess table
    for round in range(6):
        guess = ''

        # loop while in row until a valid guess is entered
        # FIXME: mess-but-works prototype standard, clean up
        while True:
            length = len(guess)

            # get input key
            # try/except here because window resize will crash getkey() without it
            try:
                key = stdscr.getkey()
            except curses.error:
                pass

            # if BACKSPACE (KEY_BACKSPACE Win/Lin; `\x7F` Mac; '\b' just in case)
            if key in ('KEY_BACKSPACE', '\x7F', '\b') and guess:
                guess = guess[:-1]
                stdscr.addstr(5 + round * 2, guess_x + (length - 1) * 4, '   ', Color.BL_WHITE)

            # if ENTER (should work cross-platform)
            elif key in ('\n', '\r'):
                scored_guess, response = wordle.submit(guess)
                if scored_guess:
                    for i, (letter, score) in enumerate(scored_guess):
                        letter = f' {letter.upper()} '
                        stdscr.addstr(5 + round * 2, guess_x + i * 4, letter, colors[score])
                    stdscr.refresh()
                    break
                else:
                    timer = popup(popup_window, timer, response)

            # if valid letter, display it in white box
            elif key in ascii_letters and length < 5:
                guess += key.lower()
                letter = f' {key.upper()} '
                stdscr.addstr(5 + round * 2, guess_x + length * 4, letter, Color.BL_WHITE)

        draw_tracker(stdscr, wordle.letter_tracker)

        # success
        if guess == wordle.answer:
            popup(popup_window, timer, response)
            break
    else:
        # game over
        popup(popup_window, timer, response)

    stdscr.getch()


curses.wrapper(main)

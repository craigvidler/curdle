import curses
from string import ascii_letters
import sys
from threading import Timer
from wordle import Wordle

# Game object. Pass in answer if required during dev
answer = sys.argv[1] if len(sys.argv) > 1 else ''
wordle = Wordle(answer)
wordle.new_game()


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
    LGREY = curses.color_pair(1) | curses.A_BOLD
    DGREY = curses.color_pair(2) | curses.A_BOLD
    YELLOW = curses.color_pair(3) | curses.A_BOLD
    GREEN = curses.color_pair(4) | curses.A_BOLD
    colors = (LGREY, DGREY, YELLOW, GREEN)

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
            color = LGREY if not tracker else colors[tracker[letter]]
            stdscr.addstr(y, tracker_x + j * 4, f' {letter.upper()} ', color)

    stdscr.refresh()


def main(stdscr):

    # set up curses
    curses.use_default_colors()  # is this necessary?
    curses.curs_set(False)  # no cursor

    # set up x-centering
    center_x = curses.COLS // 2
    guess_width = 19
    guess_x = center_x - guess_width // 2

    # set up colours
    curses.init_pair(1, 234, 250)  # very dark grey/light grey
    curses.init_pair(2, 255, 239)  # white/dark grey
    curses.init_pair(3, 255, 136)  # white/yellow
    curses.init_pair(4, 255, 28)  # white/green
    curses.init_pair(5, 234, 255)  # dark grey/white
    curses.init_pair(6, 249, 239)  # mid grey/dark grey

    LGREY = curses.color_pair(1) | curses.A_BOLD
    DGREY = curses.color_pair(2) | curses.A_BOLD
    YELLOW = curses.color_pair(3) | curses.A_BOLD
    GREEN = curses.color_pair(4) | curses.A_BOLD
    WHITE = curses.color_pair(5) | curses.A_BOLD
    MGREY = curses.color_pair(6)

    colors = (LGREY, DGREY, YELLOW, GREEN)

    # title bar
    title = 'curdle'
    stdscr.addstr(0, 0, ' ' * curses.COLS, DGREY)
    stdscr.addstr(0, center_x - len(title) // 2, title, DGREY)

    # menu. FIXME FFS
    menu = '<esc> for menu'
    stdscr.addstr(0, curses.COLS - len(menu) - 1, '', DGREY)

    for item in menu.split(' '):
        if item == '<esc>':
            stdscr.addstr(item, DGREY)
        else:
            stdscr.addstr(' ' + item, MGREY)

    # set up guesses board
    for i in range(6):
        y = 5 + i * 2
        for j in range(5):
            stdscr.addstr(y, guess_x + j * 4, '   ', WHITE)

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
                stdscr.addstr(5 + round * 2, guess_x + (length - 1) * 4, '   ', WHITE)

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
                stdscr.addstr(5 + round * 2, guess_x + length * 4, letter, WHITE)

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

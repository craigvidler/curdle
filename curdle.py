import curses
import curses.ascii  # need to import specifically or it won't be found
from string import ascii_letters
from wordle import Wordle

wordle = Wordle()
wordle.new_game()


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
        y = 18 + i * 2
        if i == 1:
            tracker_x += 2
        if i == 2:
            tracker_x += 4
        for j, letter in enumerate(row):
            # if tracker:
            #     print(tracker[letter])
            color = LGREY if not tracker else colors[tracker[letter].value]
            stdscr.addstr(y, tracker_x + j * 4, f' {letter.upper()} ', color)


def main(stdscr):

    # set up curses
    curses.use_default_colors()
    curses.curs_set(False)

    # set up centring
    center_x = curses.COLS // 2
    guess_width = 19
    guess_x = center_x - guess_width // 2

    # set up colours
    curses.init_pair(1, 232, 250)  # very dark grey/light grey
    curses.init_pair(2, 255, 239)  # white/dark grey
    curses.init_pair(3, 255, 136)  # white/yellow
    curses.init_pair(4, 255, 28)  # white/green
    curses.init_pair(5, 239, 255)  # dark grey/white
    curses.init_pair(6, 247, 239)  # mid grey/dark grey

    LGREY = curses.color_pair(1) | curses.A_BOLD
    DGREY = curses.color_pair(2) | curses.A_BOLD
    YELLOW = curses.color_pair(3) | curses.A_BOLD
    GREEN = curses.color_pair(4) | curses.A_BOLD
    WHITE = curses.color_pair(5) | curses.A_BOLD
    MGREY = curses.color_pair(6)
    DGREY_NO_BOLD = curses.color_pair(2)

    colors = (LGREY, DGREY, YELLOW, GREEN)

    # title bar
    title = 'curdle'
    stdscr.addstr(0, 0, ' ' * curses.COLS, DGREY)
    stdscr.addstr(0, center_x - len(title) // 2, title, DGREY)

    # menu. FIXME FFS
    menu = 'help  stats  quit'
    stdscr.addstr(0, curses.COLS - len(menu) - 1, '', DGREY)
    menu = ('h', 'elp', '  ', 's', 'tats', '  ', 'q', 'uit')
    for item in menu:
        if len(item) == 1:
            stdscr.addstr(item, DGREY_NO_BOLD)
        else:
            stdscr.addstr(item, MGREY)

    # set up guesses board
    for i in range(6):
        y = 5 + i * 2
        for j in range(5):
            stdscr.addstr(y, guess_x + j * 4, '   ', WHITE)

    # set up letter tracker
    draw_tracker(stdscr)

    stdscr.addstr(2, 0, wordle.answer)

    # for each row in guess table
    for round in range(6):
        # input a guess
        guess = ''

        # loop while in row until a valid guess is entered
        while True:
            length = len(guess)
            letter = stdscr.getkey()

            # Both BS and DEL needed? What about curses.KEY_BACKSPACE (263)?
            # Arrows keys send eg 'KEY_LEFT'; first check filters them out.
            if len(letter) == 1 and ord(letter) in (curses.ascii.BS, curses.ascii.DEL) and guess:
                guess = guess[:-1]
                stdscr.addstr(5 + round * 2, guess_x + (length - 1) * 4, '   ', LGREY)

            # '\n' cross-platform? What about curses.KEY_ENTER?
            elif letter == '\n' and length == 5:
                scored_guess = wordle.submit(guess)
                if scored_guess:
                    for i, (letter, score) in enumerate(scored_guess):
                        letter = f' {letter.upper()} '
                        stdscr.addstr(5 + round * 2, guess_x + i * 4, letter, colors[score.value])
                    break

            elif letter in ascii_letters and length < 5:
                guess += letter
                letter = f' {letter.upper()} '
                stdscr.addstr(5 + round * 2, guess_x + length * 4, letter, DGREY)

        draw_tracker(stdscr, wordle.letter_tracker)

        if guess == wordle.answer:
            break


curses.wrapper(main)

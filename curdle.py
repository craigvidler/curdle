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
            color = LGREY if not tracker else colors[tracker[letter]]
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
    curses.init_pair(1, 232, 250)  # black/light grey
    curses.init_pair(2, 255, 239)  # white/dark grey
    curses.init_pair(3, 255, 214)  # white/yellow
    curses.init_pair(4, 255, 28)  # white/green

    LGREY = curses.color_pair(1) | curses.A_BOLD
    DGREY = curses.color_pair(2) | curses.A_BOLD
    YELLOW = curses.color_pair(3) | curses.A_BOLD
    GREEN = curses.color_pair(4) | curses.A_BOLD

    colors = (LGREY, DGREY, YELLOW, GREEN)

    # set up guesses board
    for i in range(6):
        y = 5 + i * 2
        for j in range(5):
            stdscr.addstr(y, guess_x + j * 4, '   ', LGREY)

    # set up letter tracker
    draw_tracker(stdscr)

    stdscr.addstr(0, 0, wordle.answer)

    for round in range(6):
        # input a guess
        guess = ''

        while True:
            length = len(guess)
            letter = stdscr.getkey()

            # Both BS and DEL needed? What about curses.KEY_BACKSPACE (263)?
            if ord(letter) in (curses.ascii.BS, curses.ascii.DEL) and guess:
                guess = guess[:-1]
                stdscr.addstr(5 + round * 2, guess_x + (length - 1) * 4, '   ', LGREY)

            # '\n' cross-platform? What about curses.KEY_ENTER?
            elif letter == '\n' and length == 5:
                break

            elif letter in ascii_letters and length < 5:
                guess += letter
                letter = f' {letter.upper()} '
                stdscr.addstr(5 + round * 2, guess_x + length * 4, letter, DGREY)

        scored_guess = wordle.submit(guess)
        # stdscr.addstr(1, 0, str(scored_guess))

        if scored_guess:
            for i, (letter, score) in enumerate(scored_guess):
                letter = f' {letter.upper()} '
                stdscr.addstr(5 + round * 2, guess_x + i * 4, letter, colors[score])

        draw_tracker(stdscr, wordle.letter_tracker)

        if guess == wordle.answer:
            break


curses.wrapper(main)

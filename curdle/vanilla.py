from collections import Counter
from itertools import groupby
import sys
from model import Wordle

# ANSI codes for background colours and text
LIGHT_GREY = '\u001b[48;5;245m'
DARK_GREY = '\u001b[48;5;239m'
YELLOW = '\u001b[48;5;136m'
GREEN = '\u001b[48;5;28m'
BG_COLORS = (LIGHT_GREY, DARK_GREY, YELLOW, GREEN)

BLACK_TEXT = '\u001b[38;5;235m'
WHITE_TEXT = '\u001b[37m'
BOLD = '\u001b[1m'
RESET = '\u001b[0m'

# Game object. Pass in answer if required during dev
answer = sys.argv[1] if len(sys.argv) > 1 else ''
wordle = Wordle(answer)
wordle.new_game()


def colorize(scored_list: list):
    """expect a list of tuple pairs [(letter, score)…], return color version"""
    output = ''
    for letter, score in scored_list:
        text_color = BLACK_TEXT if not score else WHITE_TEXT
        bg_color = BG_COLORS[score]
        output += f'{bg_color}{BOLD}{text_color} {letter.upper()} {RESET}'
    return output


def menu():
    while True:
        command = input('[N]ew game, [S]tats, or [Q]uit: ').lower()
        if command == 'q':
            raise SystemExit()
        if command == 's':
            print(format_stats(wordle.scores))
        elif command == 'n':
            wordle.new_game()
            break


def format_stats(scores: list):
    """Turn wordle.scores into printable output."""

    # Eg `scores` might equal [0, 0, 4, 6, 0, 3], meaning game 1 lost, game 2
    # lost, game 3 won in turn 4, game 4 won in turn 6, game 5 lost, game 6
    # won in turn 3. `streaks` would then equal [0, 2, 0, 1]. (Retain zeroes
    # since current streak might be 0.)

    # total number of games
    played = len(scores)

    # positive numbers as a %age of all numbers
    win_percent = round(sum(game > 0 for game in scores) / played * 100)

    # stats grouped into summed streaks and zeros
    grouped = groupby(scores, lambda x: x > 0)
    streaks = [sum(1 for _ in group) if key else 0 for key, group in grouped]

    label_style = f'{LIGHT_GREY}{BLACK_TEXT}'
    value_style = f'{DARK_GREY}{BOLD}{WHITE_TEXT}'

    return (
        '\n'
        f'{label_style} Played {value_style} {played} {RESET}   '
        f'{label_style} Win % {value_style} {win_percent} {RESET}   '
        f'{label_style} Current streak {value_style} {streaks[-1]} {RESET}   '
        f'{label_style} Max streak {value_style} {max(streaks)} {RESET}\n\n'
        f'Guess distribution: \n\n'
        f'{histo(scores)}'
    )


def histo(scores: list):
    """Turn wordle.scores into a histogram"""

    MAX_SIZE = 24
    output = ''
    totals = Counter(scores)

    # extract biggest value (ie most common score) upfront (other bars sized
    # proportionally to it). Provide a default in case there's no non-zero
    # score yet (`max([])` causes error).
    biggest = max([v for k, v in totals.items() if k > 0], default=1)

    # Ensure all keys 1-6 are present, with a 0 default val
    for k, v in [(i, totals.get(i, 0)) for i in range(1, 7)]:
        # latest score highlighted in green
        bg_color = GREEN if k == scores[-1] else DARK_GREY
        spaces = ' ' * round(MAX_SIZE * (v / biggest))  # size the bar
        output += f' {k} {bg_color}{spaces}{WHITE_TEXT} {v} {RESET}\n'

    return output


def main():
    """main loop, manages interface between UI and wordle object"""

    # loop every turn
    while wordle.state == 'playing':

        # input
        guess = input(f'Guess #{wordle.turn }: ').lower()

        # submit input; output error message if any
        scored_guess, response = wordle.submit(guess)
        if not scored_guess:
            print(response, '\n')
            continue

        # output colored guess and updated tracker if valid guess
        print(colorize(scored_guess), '  ', end='')
        print(colorize(wordle.tracker.items()), '\n')

        # output message if solved or game over, enable menu
        if wordle.state != 'playing':
            print(response)
            menu()


if __name__ == '__main__':
    main()

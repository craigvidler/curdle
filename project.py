from wordle import Wordle
from itertools import groupby
from collections import Counter

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

# game object
wordle = Wordle()
wordle.new_game()


def output(scored_list: list, end: str):
    for letter, score in scored_list:
        text_color = BLACK_TEXT if score.name == 'UNGUESSED' else WHITE_TEXT
        bg_color = BG_COLORS[score.value]
        print(f'{bg_color}{BOLD}{text_color} {letter.upper()} {RESET}', end='')
    print(end, end='')


def menu():
    while True:
        command = input('[N]ew game, [S]tats, or [Q]uit: ').lower()
        if command == 'q':
            raise SystemExit()
        if command == 's':
            print(format_stats(wordle.stats))
        elif command == 'n':
            wordle.new_game()
            break


def format_stats(stats: list):
    """Turn wordle.stats into printable output."""

    # Eg `stats` might equal [0, 0, 4, 6, 0, 3], meaning game 1 lost, game 2
    # lost, game 3 won in round 4, game 4 won in round 6, game 5 lost, game 6
    # won in round 3. `streaks` would then equal [0, 2, 0, 1]. (Retain zeroes
    # since current streak might be 0.)

    # total number of games
    played = len(stats)

    # positive numbers as a %age of all numbers
    win_percent = round(sum(game > 0 for game in stats) / played * 100)

    # stats grouped into summed streaks and zeros
    grouped = groupby(stats, lambda x: x > 0)
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
        f'{histo(stats)}'
    )


def histo(stats: list):
    """Turn wordle.stats into a histogram"""

    MAX_SIZE = 24
    output = ''
    totals = Counter(stats)

    # extract biggest value upfront, bars sized proportionally to it
    biggest = max(v for k, v in totals.items() if k > 0)

    # Ensure all keys 1-6 are present, with a 0 default val
    for k, v in [(i, totals.get(i, 0)) for i in range(1, 7)]:
        # latest score highlighted in green
        bg_color = GREEN if k == stats[-1] else DARK_GREY
        spaces = ' ' * round(MAX_SIZE * (v / biggest))  # size the bar
        output += f' {k} {bg_color}{spaces}{WHITE_TEXT} {v} {RESET}\n'

    return output


def main():

    while wordle.round <= wordle.max_rounds:
        if wordle.round == 1:
            print(wordle.answer)  # for testing, remove for production
        guess = input(f'Guess #{wordle.round}: ').lower()

        scored_guess = wordle.submit(guess)
        if not scored_guess:
            print('Not a valid word\n')
            continue

        # output() expects a list of tuple pairs in the form
        # [(letter, score)…], plus any end output.
        output(scored_guess, end='   ')
        output(wordle.letter_tracker.items(), end='\n\n')

        # check whether solved or game over
        if wordle.status == 'solved':
            print('Correct! ', end='')
        elif wordle.status == 'game over':
            print(f'Game over. The answer was "{wordle.answer}". ', end='')

        # menu if not playing
        if wordle.status != 'playing':
            menu()


if __name__ == '__main__':
    main()

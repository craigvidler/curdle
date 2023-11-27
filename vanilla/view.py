from curdle.config import AppStatus, Error
from itertools import zip_longest

# ANSI codes for background colours and text
LIGHT_GREY = '\u001b[48;5;253m'
GREY = '\u001b[48;5;245m'
DARK_GREY = '\u001b[48;5;239m'
YELLOW = '\u001b[48;5;136m'
GREEN = '\u001b[48;5;28m'

BLACK_TEXT = '\u001b[38;5;235m'
WHITE_TEXT = '\u001b[37m'
BOLD = '\u001b[1m'
RESET = '\u001b[0m'

# A mapping of eg GREEN to 3 etc for letter scores. L GREY for blanks.
BG_COLORS = (GREY, DARK_GREY, YELLOW, GREEN, LIGHT_GREY)


def colorize(scored_list: list):
    """expect a list of tuple pairs [(letter, score)…], return color version."""
    output = ''
    for letter, score in scored_list:
        text_color = BLACK_TEXT if not score else WHITE_TEXT
        bg_color = BG_COLORS[score]
        output += f'{bg_color}{BOLD}{text_color} {letter.upper()} {RESET} '
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


class View:
    def __init__(self, model):

        # Observer pattern: model will call update() when state changed
        model.attach(self)

    def get_input(self, callback, turn):
        guess = input(f'Round {turn}: ').lower()
        callback(guess)

    def draw_alert(self, alert):
        spaces = (40 // 2 - len(alert) // 2) * ' '
        print(spaces + alert)

    def update(self, wordle):

        # if no error
        if not isinstance(wordle.alert, Error):
            self.draw_guesses(wordle)
            self.draw_alert(str(wordle.alert))
            self.draw_qwerty(wordle.qwerty)
        else:
            print(wordle.alert)

        # enable menu if solved or game over
        if wordle.app_status is AppStatus.PLAYING:
            menu()

    def draw_guesses(self, wordle):
        unguessed = [(' ', -1)] * 5
        turns = range(wordle.MAX_TURNS)
        previous = wordle.previous_guesses

        print()
        for _, guess in zip_longest(turns, previous, fillvalue=unguessed):
            print('          ', colorize(guess))
            print()

    def draw_qwerty(self, qwerty):
        print()
        for i, row in enumerate(qwerty):
            spaces = ('', '  ', '      ')
            print(spaces[i], colorize(row))
            print()

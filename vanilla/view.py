from curdle.config import AppStatus, Error, MenuOption
from itertools import zip_longest

# ANSI codes for background colours and text
LIGHT_GREY = '\u001b[48;5;253m'
GREY = '\u001b[48;5;245m'
DARK_GREY = '\u001b[48;5;239m'
YELLOW = '\u001b[48;5;136m'
GREEN = '\u001b[48;5;28m'
RED = '\u001b[48;5;124m'

BLACK_TEXT = '\u001b[38;5;235m'
WHITE_TEXT = '\u001b[37m'
BOLD = '\u001b[1m'
RESET = '\u001b[0m'

# A mapping of eg GREEN to 3 etc for letter scores. L GREY for blanks.
BG_COLORS = (GREY, DARK_GREY, YELLOW, GREEN, LIGHT_GREY)


class View:
    def __init__(self, model):

        # Observer pattern: model will call update() when state changed
        model.attach(self)

    def colorize(self, scored_list: list):
        """expect a list of tuple pairs [(letter, score)…], return color version."""
        output = ''
        for letter, score in scored_list:
            text_color = BLACK_TEXT if not score else WHITE_TEXT
            bg_color = BG_COLORS[score]
            output += f'{bg_color}{BOLD}{text_color} {letter.upper()} {RESET} '
        return output

    def menu(self):
        prompt = []
        options = {}
        for option in MenuOption:
            label = str(option)
            options[label[0].lower()] = option
            prompt.append(f'[{label[0]}]{label[1:].lower()}')
        prompt = ", ".join(prompt)
        key = input(f'{prompt}: ')
        return options.get(key, None)

    def get_input(self, callback, turn):
        guess = input(f'Round {turn}: ').lower()
        callback(guess)

    def draw_alert(self, alert):
        if alert:
            spaces = (38 // 2 - len(alert) // 2) * ' '
            alert = f'{spaces}{RED} {alert} {RESET}'
        else:
            alert = ''
        print(alert)

    def update(self, wordle):

        # if error
        if isinstance(wordle.alert, Error):
            print(wordle.alert)
        else:
            self.draw_guesses(wordle)
            self.draw_alert(str(wordle.alert))
            self.draw_qwerty(wordle.qwerty)

    def draw_guesses(self, wordle):
        blank_row = [(' ', -1)] * 5  # -1 == LIGHT_GREY
        turns = range(wordle.MAX_TURNS)
        previous = wordle.previous_guesses

        print('\n')
        for _, guess in zip_longest(turns, previous, fillvalue=blank_row):
            print('          ', self.colorize(guess))
            print()

    def draw_qwerty(self, qwerty):
        print()
        for i, row in enumerate(qwerty):
            spaces = ('', '  ', '      ')
            print(spaces[i], self.colorize(row))
            print()

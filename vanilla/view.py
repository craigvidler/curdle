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


def colorize(scored_list: list):
    """expect a list of tuple pairs [(letter, score)…], return color version."""
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


# def main():
#     """main loop, manages interface between UI and wordle object"""

#     # loop every turn
#     while wordle.state == 'playing':

#         # input
#         guess = input(f'Guess #{wordle.turn }: ').lower()

#         # submit input; output error message if any
#         scored_guess, response = wordle.submit(guess)
#         if not scored_guess:
#             print(response, '\n')
#             continue

#         # output colored guess and updated tracker if valid guess
#         print(colorize(scored_guess), '  ', end='')
#         print(colorize(wordle.tracker.items()), '\n')


class View:
    def __init__(self, model):

        # Observer pattern: model will call update() when state changed
        model.attach(self)

    def update(self, wordle):

        # output colored guess and updated tracker if valid guess
        if not wordle.alert:
            print('       ', colorize(wordle.previous_guesses[-1]), '\n')
            for i, row in enumerate(wordle.qwerty):
                spaces = ('', ' ', '    ')
                print(spaces[i], colorize(row))
        else:
            print(wordle.alert)

        # output message if solved or game over, enable menu
        if wordle.app_status != 'playing':
            # print(wordle.alert)
            menu()

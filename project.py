from wordle import Wordle

# Global constants
BG_COLOURS = (
    '\u001b[48;5;245m',  # LIGHT GREY
    '\u001b[48;5;239m',  # DARK GREY
    '\u001b[48;5;11m',  # YELLOW
    '\u001b[48;5;28m'  # GREEN
)
BLACK_TEXT = '\u001b[30m'
WHITE_TEXT = '\u001b[37;1m'
RESET = '\u001b[0m'

# game object
wordle = Wordle()
wordle.new_game()


def output(scored_list, end):
    for letter, status in scored_list:
        text_colour = BLACK_TEXT if status == 0 else WHITE_TEXT
        print(f'{BG_COLOURS[status]}{text_colour} {letter.upper()} {RESET}', end='')
    print(end, end='')


def menu():
    while True:
        command = input('[N]ew game, or [Q]uit: ').lower()
        if command == 'q':
            raise SystemExit()
        elif command == 'n':
            wordle.new_game()
            break


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
        # [(letter, status)…], plus any end output.
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

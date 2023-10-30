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


def output(scored_list, end):
    for letter, status in scored_list:
        text_colour = BLACK_TEXT if status == 0 else WHITE_TEXT
        print(f'{BG_COLOURS[status]}{text_colour} {letter.upper()} {RESET}', end='')
    print(end, end='')


def main():
    wordle = Wordle()
    wordle.new_game()

    print(wordle.answer)  # for testing, remove for production
    while wordle.round <= wordle.max_rounds:
        guess = input(f'Guess #{wordle.round}: ').lower()

        scored_guess = wordle.submit(guess)
        if not scored_guess:
            print('Not a valid word\n')
            continue

        # output() expects a list of tuple pairs in the form
        # [(letter, status)…], plus any end output.
        output(scored_guess, end='   ')
        output(wordle.letter_tracker.items(), end='\n\n')

        # Check whether solved
        if guess == wordle.answer:
            print('Correct!')
            raise SystemExit()

    # Word not guessed, game over
    print(f'Game over. The answer was "{wordle.answer}".')


if __name__ == '__main__':
    main()

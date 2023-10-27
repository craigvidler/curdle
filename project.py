from random import choice
from string import ascii_lowercase


def get_valid_guesses():
    with open('data/valid_guesses.txt') as f:
        return set(f.read().splitlines())


def choose_answer():
    with open('data/valid_answers.txt') as f:
        return choice(f.read().splitlines())


def get_guess(attempt, valid_guesses):
    guess = input(f'Guess #{attempt}: ').lower()
    return guess if guess in valid_guesses else None


def score(guess, answer):
    # Start by setting all letters to grey by default. Copy answer to a list
    # so we can delete letters as we go to avoid counting dupes.
    scored_guess = [(letter, 'DARK_GREY') for letter in guess]
    answer_letters = list(answer)

    # first find any green letters
    for i, (a, b) in enumerate(zip(guess, answer_letters)):
        if a == b:
            scored_guess[i] = (a, 'GREEN')
            answer_letters[i] = ''

    # then find any yellows
    for i, (_, colour) in enumerate(scored_guess):
        if colour == 'DARK_GREY':
            if guess[i] in answer_letters:
                scored_guess[i] = (guess[i], 'YELLOW')
                answer_letters[answer_letters.index(guess[i])] = ''  # nasty

    return scored_guess


def output(scored_guess, letter_tracker):
    bg_colours = {
        'GREY': '\u001b[48;5;245m',
        'GREEN': '\u001b[48;5;28m',
        'YELLOW': '\u001b[48;5;11m',
        'DARK_GREY': '\u001b[48;5;239m'
    }
    black_text = '\u001b[30m'
    white_text = '\u001b[37;1m'
    bold = '\u001b[1m'
    reset = '\u001b[0m'

    # Ugly duplication here. Refactor?
    for letter, colour in scored_guess:
        text_colour = black_text if colour == 'GREY' else white_text
        print(f'{bg_colours[colour]}{bold}{text_colour} {letter.upper()} {reset}', end='')
    print(f'   ', end='')
    for letter, colour in letter_tracker.items():
        text_colour = black_text if colour == 'GREY' else white_text
        print(f'{bg_colours[colour]}{text_colour} {letter.upper()} {reset}', end='')
    print('\n')


def update_tracker(scored_guess, letter_tracker):
    # This works but is clunky. Numeric status codes would be easier to compare.
    for letter, colour in scored_guess:
        if letter_tracker[letter] == 'GREY':
            letter_tracker[letter] = colour
        if letter_tracker[letter] == 'DARK_GREY' and colour in ('YELLOW', 'GREEN'):
            letter_tracker[letter] = colour
        if letter_tracker[letter] == 'YELLOW' and colour == 'GREEN':
            letter_tracker[letter] = colour

    return letter_tracker


def main():
    valid_guesses = get_valid_guesses()
    answer = choose_answer()
    letter_tracker = {letter: 'GREY' for letter in ascii_lowercase}

    attempt = 1
    max_attempts = 6

    print(answer)
    while attempt <= max_attempts:
        guess = get_guess(attempt, valid_guesses)
        if not guess:
            print('Not a valid word\n')
            continue
        scored_guess = score(guess, answer)
        letter_tracker = update_tracker(scored_guess, letter_tracker)
        output(scored_guess, letter_tracker)

        # Check whether solved
        if guess == answer:
            print('Correct!')
            raise SystemExit()

        attempt += 1

    # Word not guessed, game over
    print(f'Game over. The answer was "{answer}".')


if __name__ == '__main__':
    main()

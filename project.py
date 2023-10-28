from random import choice
from string import ascii_lowercase

# Globals
BG_COLOURS = (
    '\u001b[48;5;245m',  # GREY
    '\u001b[48;5;239m',  # DARK GREY
    '\u001b[48;5;11m',  # YELLOW
    '\u001b[48;5;28m'  # GREEN
)
BLACK_TEXT = '\u001b[30m'
WHITE_TEXT = '\u001b[37;1m'
RESET = '\u001b[0m'


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
    # It's a little tricky to cover all various possible combinations of
    # duplicate and non-duplicate letters. The procedure below
    # (two-pass, status 3/green then status 2/yellow, deletions from answer)
    # is one solution; there might be a nicer way.

    # (a) Start by defaulting all letters in guess to status 1 (ie guessed
    # (dark grey). (b) Can't use a dict since duplicate letters in guess
    # would cause duplicate keys. (c) Copy answer to a list so we can delete
    # letters as we go to avoid counting dupes.
    scored_guess = [(letter, 1) for letter in guess]
    answer_letters = list(answer)

    # First find any present and well-located letters (ie green). Mark them
    # status 3 in `scored_guess` and remove from `answer_letters`
    for i, (guess_letter, answer_letter) in enumerate(zip(guess, answer_letters)):
        if guess_letter == answer_letter:
            scored_guess[i] = (guess_letter, 3)
            answer_letters[i] = ''  # remove letter but maintain structure

    # Then (ignoring letters already marked status 3), find present but not
    # well-located letters (ie yellow). Mark them status 2 in `scored_guess`
    # and remove from `answer_letters`.
    for i, (guess_letter, status) in enumerate(scored_guess):
        if guess_letter in answer_letters and status != 3:
            scored_guess[i] = (guess_letter, 2)
            answer_letters.remove(guess_letter)  # ok to change structure here

    return scored_guess


def output(scored_list):
    for letter, status in scored_list:
        text_colour = BLACK_TEXT if status == 0 else WHITE_TEXT
        print(f'{BG_COLOURS[status]}{text_colour} {letter.upper()} {RESET}', end='')


def update_tracker(scored_guess, letter_tracker):
    # Update tracker with each letter from `scored_guess`. In the tracker,
    # letters maintain their highest status reached hitherto, so only change
    # a letter's status if it's to a higher one (0/unguessed/light grey ->
    # 1/guessed/dark grey -> 2/present/yellow -> 3/located/green).
    for letter, status in scored_guess:
        if status > letter_tracker[letter]:
            letter_tracker[letter] = status

    return letter_tracker


def main():
    valid_guesses = get_valid_guesses()
    answer = choose_answer()
    # Initialise tracker letters at status 0 (ie unchosen/light grey)
    # Note letter_tracker is a dict (cf scored_guess, a list of tuples)
    letter_tracker = {letter: 0 for letter in ascii_lowercase}

    attempt = 1
    max_attempts = 6

    print(answer)  # for testing, remove for production
    while attempt <= max_attempts:
        guess = get_guess(attempt, valid_guesses)
        if not guess:
            print('Not a valid word\n')
            continue

        scored_guess = score(guess, answer)
        letter_tracker = update_tracker(scored_guess, letter_tracker)

        # (a) Output expects a list of tuple pairs in the form
        # [(letter, status)…]. (b) Fiddly presentation details like this
        # should be factored out of the main loop.
        output(scored_guess)
        print(f'   ', end='')
        output(letter_tracker.items())
        print('\n')

        # Check whether solved
        if guess == answer:
            print('Correct!')
            raise SystemExit()

        attempt += 1

    # Word not guessed, game over
    print(f'Game over. The answer was "{answer}".')


if __name__ == '__main__':
    main()

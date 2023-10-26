from random import choice


def valid_guesses():
    with open('data/guesses.txt') as f:
        return set(f.read().splitlines())


def choose_answer():
    with open('data/answers.txt') as f:
        return choice(f.read().splitlines())


MAX_ATTEMPTS = 6
GUESSES = valid_guesses()
ANSWER = choose_answer()


def get_guess(attempt):
    guess = input(f'Attempt #{attempt}: ').lower()
    return guess if guess in GUESSES else False


def score(guess):
    # set letters to grey by default, cast answer to list so we can delete
    # letters as we go to avoid counting dupes
    scored_guess = [(letter, 'GREY') for letter in guess]
    answer_letters = list(ANSWER)

    for index, letter in enumerate(guess):

        # letter located correctly (green)
        if letter == answer_letters[index]:
            scored_guess[index] = (letter, 'GREEN')
            answer_letters[index] = ''

        # letter present but not located correctly (yellow)
        elif letter in answer_letters:
            scored_guess[index] = (letter, 'YELLOW')
            answer_letters[answer_letters.index(letter)] = ''

    return scored_guess


def output(scored_guess):
    colours = {
        'GREEN': '\u001b[48;5;28m',
        'YELLOW': '\u001b[48;5;11m',
        'GREY': '\u001b[48;5;239m'
    }
    bold = '\u001b[1m'
    reset = '\u001b[0m'

    greens = 0
    for letter, colour in scored_guess:
        print(f'{colours[colour]}{bold} {letter.upper()} {reset}', end='')
        if colour == 'GREEN':
            greens += 1
    print()

    # If all chars located correctly (all green)
    if greens == len(scored_guess):
        print('Correct!')
        raise SystemExit()


def main():
    attempt = 1
    print(ANSWER)
    while attempt <= MAX_ATTEMPTS:
        guess = get_guess(attempt)
        if not guess:
            print('Not a valid word')
            continue
        scored_guess = score(guess)
        output(scored_guess)

        attempt += 1

    # Word not guessed, game over
    print(f"Game over. The word was '{ANSWER}'.")


if __name__ == '__main__':
    main()

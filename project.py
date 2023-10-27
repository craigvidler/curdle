from random import choice


def get_valid_guesses():
    with open('data/valid_guesses.txt') as f:
        return set(f.read().splitlines())


def choose_answer():
    with open('data/valid_answers.txt') as f:
        return choice(f.read().splitlines())


def get_guess(attempt, valid_guesses):
    guess = input(f'Attempt #{attempt}: ').lower()
    return guess if guess in valid_guesses else False


def score(guess, answer):
    # Start by setting all letters to grey by default. Copy answer to a list
    # so we can delete letters as we go to avoid counting dupes.
    scored_guess = [(letter, 'GREY') for letter in guess]
    answer_letters = list(answer)

    # first find any green letters
    for i, (a, b) in enumerate(zip(guess, answer_letters)):
        if a == b:
            scored_guess[i] = (a, 'GREEN')
            answer_letters[i] = ''

    # then find any yellows
    for i, (_, colour) in enumerate(scored_guess):
        if colour == 'GREY':
            if guess[i] in answer_letters:
                scored_guess[i] = (guess[i], 'YELLOW')
                answer_letters[answer_letters.index(guess[i])] = ''  # nasty

    return scored_guess


def output(scored_guess):
    colours = {
        'GREEN': '\u001b[48;5;28m',
        'YELLOW': '\u001b[48;5;11m',
        'GREY': '\u001b[48;5;239m'
    }
    bold = '\u001b[1m'
    reset = '\u001b[0m'

    for letter, colour in scored_guess:
        print(f'{colours[colour]}{bold} {letter.upper()} {reset} ', end='')
    print('\n')


def main():
    valid_guesses = get_valid_guesses()
    answer = choose_answer()

    attempt = 1
    max_attempts = 6

    print(answer)
    while attempt <= max_attempts:
        guess = get_guess(attempt, valid_guesses)
        if not guess:
            print('Not a valid word\n')
            continue
        scored_guess = score(guess, answer)
        output(scored_guess)

        # Check whether solved
        if guess == answer:
            print('Correct!')
            raise SystemExit()

        attempt += 1

    # Word not guessed, game over
    print(f'Game over. The word was "{answer}".')


if __name__ == '__main__':
    main()

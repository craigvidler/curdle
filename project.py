from random import choice

BG_GREEN = '\u001b[48;5;28m'
BG_YELLOW = '\u001b[48;5;11m'
BG_GREY = '\u001b[48;5;239m'
BOLD = '\u001b[1m'
RESET = '\u001b[0m'

attempt = 1
attempts = 6

with open('data/guesses.txt') as g, open('data/answers.txt') as a:
    guesses = set(g.read().splitlines())
    answer = choice(a.read().splitlines())

while attempt <= attempts:

    # Get input
    guess = input(f'Attempt #{attempt}: ').lower()

    if guess not in guesses:
        print('Not a valid word')
        continue

    # `answer` cast to list as we want to delete found letters. Given answer
    # of eg 'coder', deletion avoids eg the second 'e' in 'erase' wrongly
    # being marked yellow.
    answer_letters = list(answer)

    for index, letter in enumerate(guess):

        # letter located correctly (green)
        if letter == answer_letters[index]:
            answer_letters[index] = ' '
            print(f'{BG_GREEN}{BOLD} {letter.upper()} {RESET} ', end='')

        # letter present but not located correctly (yellow)
        elif letter in answer_letters:
            answer_letters[answer_letters.index(letter)] = ' '
            print(f'{BG_YELLOW}{BOLD} {letter.upper()} {RESET} ', end='')

        # letter not present at all (grey)
        else:
            print(f'{BG_GREY}{BOLD} {letter.upper()} {RESET} ', end='')
    print()

    # If all chars located correctly (all green)
    if guess == answer:
        print('Correct!')
        raise SystemExit()

    attempt += 1

# Word not guessed, game over
print(f"Game over. The word was '{answer}'.")

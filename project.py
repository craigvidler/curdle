from random import choice

with open('data/guesses.txt') as g, open('data/answers.txt') as a:
    guesses = set(g.read().splitlines())
    answer = choice(a.read().splitlines())

attempt = 1
attempts = 6

while attempt <= attempts:

    # Get input
    guess = input(f'Attempt #{attempt}: ').lower()

    if guess not in guesses:
        print('Not a valid word')
        continue

    # If all chars located correctly (all green)
    if guess == answer:
        print('Correct!')
        raise SystemExit()

    # `answer` cast to list as we want to delete found letters. Given answer
    # of eg 'coder', deletion avoids eg the second 'e' in 'erase' wrongly
    # being marked yellow.
    answer_letters = list(answer)

    for index, letter in enumerate(guess):

        # letter located correctly (green)
        if letter == answer_letters[index]:
            answer_letters[index] = ' '
            print(f'{letter}: green')

        # letter present but not located correctly (yellow)
        elif letter in answer_letters:
            answer_letters[answer_letters.index(letter)] = ' '
            print(f'{letter}: yellow')

        # letter not present at all (grey)
        else:
            print(f'{letter}: grey')

    attempt += 1

# Word not guessed, game over
print(f"Game over. The word was '{answer}'.")

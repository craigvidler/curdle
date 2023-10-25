target = 'coder'
rounds = 6

for i in range(rounds):

    # Get input
    guess = input(f'Guess #{i + 1}: ').lower()

    # If all chars located correctly (all green)
    if guess == target:
        print('Word correct!')
        raise SystemExit()

    # `target` cast to list as we want to delete found letters. Given target
    # of eg 'coder', deletion avoids eg the second 'e' in 'erase' wrongly
    # being marked yellow.
    target_letters = list(target)

    for i, letter in enumerate(guess):

        # if this letter located correctly (green letter)
        if letter == target_letters[i]:
            target_letters[i] = ' '
            print(f'{letter}: correct')

        # if this letter present but not located correctly (yellow letter)
        elif letter in target_letters:
            target_letters[target_letters.index(letter)] = ' '
            print(f'{letter}: present, wrongly located')

        # if this letter not found at all
        else:
            print(f'{letter}: not present')

# Word not guessed, game over
print(f"Game over. The word was '{target}'.")

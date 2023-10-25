target = 'coder'
attempts = 6

for i in range(attempts):
    guess = input(f'Guess #{i + 1}: ').lower()
    if guess == target:
        print('CORRECT')
        break
else:
    print('GAME OVER')

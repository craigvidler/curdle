from random import shuffle
from string import ascii_lowercase


class Wordle:

    def __init__(self):
        self.round = 0
        self.max_rounds = 6
        self.valid_guesses = set(self.load_wordlist('data/valid_guesses.txt'))
        self.valid_answers = self.load_wordlist('data/valid_answers.txt')
        shuffle(self.valid_answers)
        self.answer = None
        self.letter_tracker = {}

    def new_game(self):
        # Initialise tracker letters at status 0 (ie unguessed/light grey)
        self.letter_tracker = {letter: 0 for letter in ascii_lowercase}
        self.answer = self.valid_answers.pop()
        self.round = 1

    def load_wordlist(self, filename):
        with open(filename) as f:
            return f.read().splitlines()

    def submit(self, guess):
        # It's a little tricky to cover all various possible combinations of
        # duplicate and non-duplicate letters. The procedure below
        # (two-pass, status 3/green then status 2/yellow, deletions from answer)
        # is one solution; there might be a nicer way.

        # (a) Start by defaulting all letters in guess to status 1 (ie guessed
        # (dark grey). (b) Can't use a dict since duplicate letters in guess
        # would cause duplicate keys. (c) Copy answer to a list so we can delete
        # letters as we go to avoid counting dupes.

        if guess not in self.valid_guesses:
            return None

        scored_guess = [(letter, 1) for letter in guess]
        answer_letters = list(self.answer)

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

        self.update_tracker(scored_guess)
        self.round += 1

        return scored_guess

    def update_tracker(self, scored_guess):
        # Update tracker with each letter from `scored_guess`. In the tracker,
        # letters maintain the highest status reached, so only change a letter's
        # status if it's to a higher one (0/unguessed/light grey ->
        # 1/guessed/dark grey -> 2/present/yellow -> 3/located/green).
        for letter, status in scored_guess:
            if status > self.letter_tracker[letter]:
                self.letter_tracker[letter] = status

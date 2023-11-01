"""
Models the core game logic of Wordle. User input and display are left to a
front end (the client code using this class).

See README.md for details.
"""

from random import shuffle
from string import ascii_lowercase


class Wordle:

    def __init__(self, answers_file='', guesses_file=''):
        """Sets up a Wordle instance. Wordlists can be overridden here."""
        self.answers_file = answers_file or 'data/valid_answers.txt'
        self.valid_answers = []  # answers handled in new_game()
        self.answer = None

        self.guesses_file = guesses_file or 'data/valid_guesses.txt'
        self.valid_guesses = set(self.load_wordlist(self.guesses_file))

        self.status = 'start'  # can also be 'playing', 'solved', 'game over'
        self.round = 0
        self.max_rounds = 6
        self.letter_tracker = {}  # record guessed letters
        self.stats = []  # record game results per session

    def load_wordlist(self, filename):
        with open(filename) as f:
            return f.read().splitlines()

    def new_game(self):
        """Set/reset here anything needed to support multiple games"""

        # initialise tracker letters at status 0 (ie unguessed/light grey)
        self.letter_tracker = {letter: 0 for letter in ascii_lowercase}

        # answers loaded here not in init, with shuffle/pop not random.choice, to
        # support arbitrarily many games with minimal answer repetition
        if not self.valid_answers:
            self.valid_answers = self.load_wordlist(self.answers_file)
            shuffle(self.valid_answers)

        self.answer = self.valid_answers.pop()
        self.round = 1
        self.status = 'playing'

    def submit(self, guess):
        """
        The core of the game: take in a guess, validate it, score it in
        comparison to the answer, return a scored guess as a list of tuples.
        """

        # validate guess
        if guess not in self.valid_guesses:
            return None

        # default all letters in guess to status 1 (ie guessed/dark grey),
        # copy answer to a list (so we can remove letters)
        scored_guess = [(letter, 1) for letter in guess]
        answer_letters = list(self.answer)

        # first find status 3 letters (ie located/green)
        for i, (guess_letter, answer_letter) in enumerate(zip(guess, answer_letters)):
            if guess_letter == answer_letter:
                scored_guess[i] = (guess_letter, 3)
                answer_letters[i] = ''  # keep list element but clear it

        # then find status 2 letters (ie present/yellow)
        for i, (guess_letter, status) in enumerate(scored_guess):
            if guess_letter in answer_letters and status != 3:
                scored_guess[i] = (guess_letter, 2)
                answer_letters.remove(guess_letter)

        # if solved or game over, change status. Record game score in stats.
        if guess == self.answer:
            self.stats.append(self.round)
            self.status = 'solved'
        elif self.round == self.max_rounds:
            self.stats.append(0)
            self.status = 'game over'

        # update tracker, increment round
        self.update_tracker(scored_guess)
        self.round += 1

        return scored_guess

    def update_tracker(self, scored_guess):
        """
        Update tracker with each letter from `scored_guess`.
        Only change a letter's status if it's to a higher one.
        """

        for letter, status in scored_guess:
            if status > self.letter_tracker[letter]:
                self.letter_tracker[letter] = status

"""
Models the core game logic of Wordle. User input and display are left to a
front end (the client code using this class).

See README.md for details.
"""

from enum import IntEnum
from random import shuffle
from string import ascii_lowercase as a_to_z


class Score(IntEnum):
    UNGUESSED = 0
    ABSENT = 1
    PRESENT = 2
    CORRECT = 3


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

        # initialise tracker letters as UNGUESSED (ie status 0/light grey)
        self.letter_tracker = {letter: Score.UNGUESSED for letter in a_to_z}

        # answers loaded here not in init, with shuffle/pop not random.choice,
        # to support arbitrarily many games with minimal answer repetition
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

        # default all letters in guess to ABSENT (1/guessed/dark grey),
        # copy answer to a list (so we can remove letters)
        scored_guess = [(letter, Score.ABSENT) for letter in guess]
        answer_letters = list(self.answer)

        # first find CORRECT letters (ie 3/green)
        for i, (guess_letter, answer_letter) in enumerate(zip(guess, self.answer)):
            if guess_letter == answer_letter:
                scored_guess[i] = (guess_letter, Score.CORRECT)
                answer_letters.remove(guess_letter)

        # then find PRESENT letters (ie 2/yellow)
        for i, (guess_letter, score) in enumerate(scored_guess):
            if guess_letter in answer_letters and score != Score.CORRECT:
                scored_guess[i] = (guess_letter, Score.PRESENT)
                answer_letters.remove(guess_letter)

        # if solved or game over, change status. Record game score in stats.
         # FIXME this doesn't belong here (?)
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
        Only change a letter's score if it's to a higher one.
        """

        for letter, score in scored_guess:
            if score > self.letter_tracker[letter]:
                self.letter_tracker[letter] = score

"""
Models the core game logic of Wordle. UI is left to a front end (the client
code using this class). See README.md for details.
"""

from enum import Enum, IntEnum
from random import shuffle
from string import ascii_lowercase as a_to_z


# Using an IntEnum so we can do > comparison, and to access the int value
# outside the module without needing to import LetterScore or use .value.
class LetterScore(IntEnum):
    UNGUESSED = 0
    ABSENT = 1
    PRESENT = 2
    CORRECT = 3

# StrEnum preferable here for ease of use (no imports or .value needed outside
# the module), but like this avoids requiring Py3.11.
class State(str, Enum):
    START = 'start'
    PLAYING = 'playing'
    GAMEOVER = 'game over'
    SOLVED = 'solved'

# As above. Also, __str__ because Errors will be output not just checked like
# States, and it avoids needing `.value` below.
class Error(str, Enum):
    TOOSHORT = 'Not enough letters'
    INVALID = 'Not in word list'

    def __str__(self):
        return self.value


class Rating(Enum):
    Genius = 1
    Magnificent = 2
    Impressive = 3
    Splendid = 4
    Great = 5
    Phew = 6


class Wordle:

    def __init__(self, answer: str = ''):
        """Set up a Wordle instance."""

        self.answers_file = 'data/valid_answers.txt'
        self.valid_answers = []  # answers handled in new_game()
        self.answer = answer

        self.guesses_file = 'data/valid_guesses.txt'
        self.valid_guesses = set(self.load_wordlist(self.guesses_file))

        self.state = State.START
        self.round = 0
        self.max_rounds = 6
        self.letter_tracker = {}  # record guessed letters
        self.stats = []  # record game results per session

    def load_wordlist(self, filename: str):
        """Load a wordlist and return it in a list."""
        with open(filename) as f:
            return f.read().splitlines()

    def new_game(self):
        """Set/reset here anything needed to support multiple games"""

        # initialise tracker letters as UNGUESSED (ie 0/light grey)
        self.letter_tracker = {letter: LetterScore.UNGUESSED for letter in a_to_z}

        # answers loaded here not in init, with shuffle/pop not random.choice,
        # to support arbitrarily many games with minimal answer repetition
        if not self.valid_answers:
            self.valid_answers = self.load_wordlist(self.answers_file)
            shuffle(self.valid_answers)

        # If an answer has been passed in, use that. Get one if not.
        self.answer = self.answer or self.valid_answers.pop()
        self.round = 1
        self.state = State.PLAYING

    def score_guess(self, guess: str):
        """
        Take a guess and compare it with the answer to score it. Return a
        scored guess, a list of tuple pairs [(letter, score)…] where score
        is either ABSENT (dark grey), PRESENT (yellow) or CORRECT (green).
        """

        # Default all letters in guess to ABSENT (1/dark grey); copy answer to
        # a list (so we can remove letters).
        scored_guess = [(letter, LetterScore.ABSENT) for letter in guess]
        answer_letters = list(self.answer)

        # first find CORRECT (3, green) letters
        for i, (guess_letter, answer_letter) in enumerate(zip(guess, self.answer)):
            if guess_letter == answer_letter:
                scored_guess[i] = (guess_letter, LetterScore.CORRECT)
                answer_letters.remove(guess_letter)

        # then find PRESENT (2, yellow) letters
        for i, (guess_letter, score) in enumerate(scored_guess):
            if guess_letter in answer_letters and score is not LetterScore.CORRECT:
                scored_guess[i] = (guess_letter, LetterScore.PRESENT)
                answer_letters.remove(guess_letter)

        return scored_guess

    def submit(self, guess: str):
        """
        Take in a guess, validate it, score it in comparison to the answer,
        return a scored guess as a list of tuples, plus a response.
        """
        response = ''
        guess = guess.lower()

        # validate guess
        if len(guess) < 5:
            return None, Error.TOOSHORT
        elif guess not in self.valid_guesses:
            return None, Error.INVALID

        # score it
        scored_guess = self.score_guess(guess)

        # update game, tracker
        response = self.update_game(scored_guess)
        self.update_tracker(scored_guess)

        return scored_guess, response

    def update_game(self, scored_guess: list):
        """
        If solved or game over, change state. Record game score in stats.
        Return appropriate response.
        """

        response = ''

        # solved
        if all(score is LetterScore.CORRECT for _, score in scored_guess):
            self.stats.append(self.round)
            self.state = State.SOLVED
            response = Rating(self.round).name

        # game over
        elif self.round == self.max_rounds:
            self.stats.append(0)
            self.state = State.GAMEOVER
            response = self.answer.upper()

        # increment round
        self.round += 1

        return response

    def update_tracker(self, scored_guess: list):
        """
        Update tracker with each letter from `scored_guess`.
        Only change a letter's score if it's to a higher one.
        """

        for letter, score in scored_guess:
            if score > self.letter_tracker[letter]:
                self.letter_tracker[letter] = score

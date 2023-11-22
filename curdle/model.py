"""
Models the core game logic of Wordle. UI is left to a front end (the client
code using this class). See README.md for details.
"""

from enum import Enum, IntEnum, auto
from random import shuffle
from string import ascii_lowercase as a_to_z


class LetterScore(IntEnum):
    # Using an IntEnum so we can do > comparison, and to access the int value
    # outside the module without importing LetterScore or using .value.
    UNGUESSED = 0
    ABSENT = 1
    PRESENT = 2
    CORRECT = 3


class State(str, Enum):
    # StrEnum preferable here for ease of use (no imports or .value needed
    # outside the module), but like this avoids requiring Py3.11.
    START = 'start'
    PLAYING = 'playing'
    GAMEOVER = 'game over'
    SOLVED = 'solved'


class Error(str, Enum):
    # As above. Also, __str__ because Errors will be output not just checked
    # like States, and it avoids needing `.value` below.
    TOOSHORT = 'Not enough letters'
    INVALID = 'Not in word list'

    def __str__(self):
        return self.value


class Rating(Enum):
    # This probably shouldn't be an enum, could move elsewhere
    Genius = 1
    Magnificent = 2
    Impressive = 3
    Splendid = 4
    Great = 5
    Phew = 6


class MenuOption(IntEnum):
    """Menu options. Provide int or string based on name as needed."""
    NEW_GAME = auto()
    STATS = auto()
    EXIT = auto()

    def __str__(self):
        return self.name.replace('_', ' ')


class Menu:
    def __init__(self):
        self.options = MenuOption
        self.selected = self.options(1)  # default to first item

    def up(self):
        if self.selected > MenuOption(1):
            self.selected = MenuOption(self.selected - 1)

    def down(self):
        if self.selected < len(MenuOption):
            self.selected = MenuOption(self.selected + 1)


class Wordle:

    def __init__(self, answer: str = ''):
        """Set up a Wordle instance."""

        self.answers_file = 'data/valid_answers.txt'
        self.valid_answers = []  # answers handled in new_game()
        self.given_answer = answer  # save answer here if passed in
        self.answer = ''  # see new_game() and comment there

        self.guesses_file = 'data/valid_guesses.txt'
        self.valid_guesses = set(self.load_wordlist(self.guesses_file))
        self.previous_guesses = []  # record of submitted, scored guesses
        self.current_guess = ''  # buffer for guess-in-progress before submit

        self.state = State.START
        self.max_turns = 6
        self.tracker = {}  # record guessed letters
        self.stats = []  # record game results per session

    @property
    def turn(self):
        """Return the current turn number, must not be > 6."""
        return min(len(self.previous_guesses) + 1, 6)

    def load_wordlist(self, filename: str):
        """Load a wordlist and return it in a list."""
        with open(filename) as f:
            return f.read().splitlines()

    def new_game(self):
        """Set/reset here anything needed to support multiple games"""

        # initialise tracker letters as UNGUESSED (ie 0/light grey)
        self.tracker = {letter: LetterScore.UNGUESSED for letter in a_to_z}

        # answers loaded here not in init, with shuffle/pop not random.choice,
        # to support arbitrarily many games with minimal answer repetition
        if not self.valid_answers:
            self.valid_answers = self.load_wordlist(self.answers_file)
            shuffle(self.valid_answers)

        # If an answer has been passed in, use that. Get one if not. Can't
        # just set `self.answer` directly in init without `given_answer`
        # buffer, or renewing answer in subsequent games prevented here.
        self.answer = self.given_answer or self.valid_answers.pop()
        self.state = State.PLAYING
        self.previous_guesses = []

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

        # if solved
        if all(score is LetterScore.CORRECT for _, score in scored_guess):
            self.stats.append(self.turn)
            self.state = State.SOLVED
            response = Rating(self.turn).name

        # if game over
        elif self.turn == self.max_turns:
            self.stats.append(0)
            self.state = State.GAMEOVER
            response = self.answer.upper()

        # save the scored guess/completed turn, reset current guess buffer
        self.previous_guesses.append(scored_guess)
        self.current_guess = ''

        return response

    def update_tracker(self, scored_guess: list):
        """
        Update tracker with each letter from `scored_guess`.
        Only change a letter's score if it's to a higher one.
        """

        for letter, score in scored_guess:
            if score > self.tracker[letter]:
                self.tracker[letter] = score

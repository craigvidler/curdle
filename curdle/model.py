"""
Models the core game logic of Wordle. As part of an MVC app, UI is left to a
front end (the client code using this class). See README.md for details.
"""

from collections import Counter
from enum import Enum, IntEnum, auto
from itertools import groupby
from random import shuffle
from string import ascii_letters, ascii_lowercase as a_to_z


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
        self.scores = []  # record game results per session

    @property
    def stats(self):
        """Turn Wordle.scores into a stats dictionary."""

        # total number of games
        played = len(self.scores)

        # positive numbers as a %age of all numbers
        win_percent = round(sum(game > 0 for game in self.scores) / played * 100)

        # scores grouped into summed streaks and zeros
        grouped = groupby(self.scores, lambda x: x > 0)
        streaks = [sum(1 for _ in group) if key else 0 for key, group in grouped]

        # distribution totals
        distribution = {i: Counter(self.scores)[i] for i in range(1, 7)}

        return {
            'Played': played,
            'Win %': win_percent,
            'Current streak': streaks[-1],
            'Max streak': max(streaks),
            'Guess distribution': distribution
        }

    @property
    def turn(self):
        """Return the current turn number, must not be > 6."""
        return min(len(self.previous_guesses) + 1, 6)

    def add_letter(self, letter):
        """Add a letter to current guess if valid to do so."""
        if letter in ascii_letters and len(self.current_guess) < 5:
            self.current_guess += letter.lower()

    def delete_letter(self, letter):
        """Delete a letter from current guess."""
        self.current_guess = self.current_guess[:-1]

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

    def submit(self, guess=''):
        """
        Validate current guess, score it, update game, return a scored guess
        as a list of tuples or None, plus a response or None.
        """

        # The default expectation is letter-by-letter submission via
        # `self.current_guess`(eg from a UI like curses), but this line and
        # default parameter will also support an override for UIs like the
        # command line which are limited to submitting the whole guess only.
        guess = guess or self.current_guess

        # validate guess: if invalid, response is Error, scored_guess is empty
        if error := self.validate(guess):
            scored_guess, response = None, error

        # else score it, update game: response returns empty, Rating or answer
        else:
            scored_guess = self.score_guess(guess)
            response = self.update_game(scored_guess)

        return scored_guess, response

    def update_game(self, scored_guess: list):
        """
        Update game elements at end of turn. If game solved or over, change
        state. Record game score in scores. Return appropriate response.
        """

        # will remain empty for a valid guess in a non-winning, non-losing turn
        response = ''

        # if solved
        if all(score is LetterScore.CORRECT for _, score in scored_guess):
            self.scores.append(self.turn)
            self.state = State.SOLVED
            response = Rating(self.turn).name

        # if game over
        elif self.turn == self.max_turns:
            self.scores.append(0)
            self.state = State.GAMEOVER
            response = self.answer.upper()

        # in all cases: update tracker, save the scored guess, reset current
        # guess buffer
        self.update_tracker(scored_guess)
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

    def validate(self, guess):
        """Validate guess: return None if valid, Error if invalid."""
        if len(guess) < 5:
            return Error.TOOSHORT
        elif guess not in self.valid_guesses:
            return Error.INVALID

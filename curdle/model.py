"""
Model the core game logic of Wordle. Designed to be used as part of an MVC
app or similar structure where UI is left to a front end (the client code
using this class). See README.md for details.
"""

from collections import Counter
from .config import AppStatus, Error, LetterScore, MenuOption, Rating
from itertools import groupby
from random import shuffle
from string import ascii_lowercase as a_to_z


class Menu:
    """Provide a game menu based on MenuOptions."""

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

        self.app_status = AppStatus.START
        self.MAX_TURNS = 6
        self.tracker = {}  # record guessed letters
        self.scores = []  # record game results per session
        self.alert = ''  # ≈ popup message to user
        self.observers = []  # for MVC with Observer pattern

    @property
    def qwerty(self):
        """Return the tracker formatted in qwerty order/layout."""
        rows = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
        return [[(letter, self.tracker[letter]) for letter in row] for row in rows]

    @property
    def stats(self):
        """Turn self.scores into a stats dictionary."""

        # Eg `stats` might equal [0, 0, 4, 6, 0, 3], meaning game 1 lost, game 2
        # lost, game 3 won in turn 4, game 4 won in turn 6, game 5 lost, game 6
        # won in turn 3. `streaks` would then equal [0, 2, 0, 1]. (Retain zeroes
        # since current streak might be 0.)

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
            'played': ('Played', played),
            'wins': ('Win %', win_percent),
            'current_streak': ('Current streak', streaks[-1]),
            'max_streak': ('Max streak', max(streaks)),
            'distribution': distribution,
            'last': self.scores[-1] if self.scores else 0
        }

    @property
    def turn(self):
        """Return the current turn number, must not be > 6."""
        return min(len(self.previous_guesses) + 1, 6)

    def attach(self, observer):  # what type hint here?
        """Enable observer to add itself to the list."""
        self.observers.append(observer)

    def check_error(self, guess: str):
        """Check for errors: return Error if invalid or None if valid."""
        if len(guess) < 5:
            return Error.TOOSHORT
        elif guess not in self.valid_guesses:
            return Error.INVALID

    def finish_turn(self, scored_guess: list):
        """
        Update game elements at end of turn. If game solved or over, change
        app_status. Record game score in scores. Return appropriate response.
        """

        # will remain empty for a valid guess in a non-winning, non-losing turn
        response = ''

        # if solved
        if all(score is LetterScore.CORRECT for _, score in scored_guess):
            self.scores.append(self.turn)
            self.app_status = AppStatus.SOLVED
            response = Rating(self.turn)

        # if game over
        elif self.turn == self.MAX_TURNS:
            self.scores.append(0)
            self.app_status = AppStatus.GAMEOVER
            response = self.answer.upper()

        # in all cases: save guess, update tracker
        self.previous_guesses.append(scored_guess)
        self.update_tracker()

        return response

    def load_wordlist(self, filename: str):
        """Load a wordlist and return it in a list."""
        with open(filename) as f:
            return f.read().splitlines()

    def new_game(self):
        """Set/reset here anything needed to support multiple games."""

        # initialise tracker letters as UNGUESSED (ie 0/light grey)
        self.tracker = {letter: LetterScore.UNGUESSED for letter in a_to_z}
        self.previous_guesses = []
        self.alert = ''

        # answers loaded here not in init, with shuffle/pop not random.choice,
        # to support arbitrarily many games with minimal answer repetition
        if not self.valid_answers:
            self.valid_answers = self.load_wordlist(self.answers_file)
            shuffle(self.valid_answers)

        # If an answer has been passed in, use that. Get one if not. Can't
        # just set `self.answer` directly in init without `given_answer`
        # buffer, or renewing answer in subsequent games prevented here.
        self.answer = self.given_answer or self.valid_answers.pop()
        self.app_status = AppStatus.PLAYING

        self.notify()  # signal game start to obervers

    def notify(self):
        """Part of MVC/Observer pattern: tell observers model has changed."""
        for observer in self.observers:
            observer.update(self)

        # write current game state to file to aid debugging (with curses esp)
        self.log()

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
        Take in guess then delegate: validate it, score it, save it, update
        game, create response if required.
        """

        # check guess for errors
        if error := self.check_error(guess):
            response = error

        # else it's valid: score it, finish turn
        else:
            scored_guess = self.score_guess(guess)
            response = self.finish_turn(scored_guess)

        self.alert = response
        self.notify()  # signal model change to observers

    def update_tracker(self):
        """
        Update tracker with each letter from `scored_guess`.
        Only change a letter's score if it's to a higher one.
        """
        for letter, score in self.previous_guesses[-1]:
            self.tracker[letter] = max(self.tracker[letter], score)

    def log(self):
        """To aid debugging"""
        with open('debug.log', 'w') as f:
            f.write(str(self))

    def __str__(self):
        return \
            f'App status: {self.app_status}\n' \
            + f'\nAnswer: {self.answer}\n' \
            + '\nPrevious guesses:\n' \
            + '\n'.join(str(guess) for guess in self.previous_guesses) \
            + '\n\nTracker:\n' \
            + ' '.join(f'{k}:{v}' for k, v in self.tracker.items())

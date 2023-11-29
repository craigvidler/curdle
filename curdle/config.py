from enum import Enum, IntEnum


class AnsiCode(str, Enum):
    LIGHT_GREY = '\u001b[48;5;253m'
    GREY = '\u001b[48;5;245m'
    DARK_GREY = '\u001b[48;5;239m'
    YELLOW = '\u001b[48;5;136m'
    GREEN = '\u001b[48;5;28m'
    RED = '\u001b[48;5;124m'

    BLACK_TEXT = '\u001b[38;5;235m'
    WHITE_TEXT = '\u001b[37m'
    BOLD = '\u001b[1m'
    RESET = '\u001b[0m'

    def __str__(self):
        return self.value


class AppStatus(str, Enum):
    """
    Encode top-level game status. StrEnum preferable here for ease of use
    (no imports or .value needed outside the module), but like this avoids
    requiring Py3.11.
    """
    START = 'start'
    PLAYING = 'playing'
    GAMEOVER = 'gameover'
    SOLVED = 'solved'
    MENU = 'menu'
    STATS = 'stats'


class Error(str, Enum):
    """
    Encode error messages. As AppStatus but also __str__ because Error will be
    output not just checked, and it avoids needing `.value` when doing so.
    """
    TOOSHORT = 'Not enough letters'
    INVALID = 'Not in word list'

    def __str__(self):
        return self.value


class LetterScore(IntEnum):
    """
    Encode the status of letters in the tracker and scored guesses (≈ grey,
    yellow, green etc). Use an IntEnum so we can do > comparison, and to
    access the int value outside the module without importing LetterScore or
    using .value.
    """
    UNGUESSED = 0
    ABSENT = 1
    PRESENT = 2
    CORRECT = 3


class MenuOption(IntEnum):
    """Encode menu options. Provide int or label based on name as needed."""
    NEW_GAME = 1
    STATS = 2
    EXIT = 3

    def __str__(self):
        return self.name.replace('_', ' ')


class Rating(Enum):
    """Map between turn number/game score, and end of solved game message."""
    GENIUS = 1
    MAGNIFICENT = 2
    IMPRESSIVE = 3
    SPLENDID = 4
    GREAT = 5
    PHEW = 6

    def __str__(self):
        return self.name.capitalize()

# For vanilla app: a mapping of eg GREEN to 3 etc for letter scores. L GREY
# (-1) for blanks.
SCORE_COLORS = (
    AnsiCode.GREY,
    AnsiCode.DARK_GREY,
    AnsiCode.YELLOW,
    AnsiCode.GREEN,
    AnsiCode.LIGHT_GREY
)

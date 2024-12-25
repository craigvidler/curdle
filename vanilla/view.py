from curdle.config import AnsiCode as Code, SCORE_COLORS, Error, MenuOption
import re

APP_WIDTH = 42


class View:
    def __init__(self, model):
        """Initiate the view object."""

        # Observer pattern: model will call self.update() when game state changed
        model.attach(self)

    def center(self, line: str):
        """
        Center a given string within the game board width. ljust/rjust or
        f-string padding won't work due to escape sequences.
        """
        stripped = re.sub(r'\x1b.*?m', '', line)  # remove ANSI codes
        left_spaces = ((APP_WIDTH - len(stripped)) // 2) * ' '
        return left_spaces + line

    def colorize(self, scored_list: list):
        """
        Expect a list of tuple pairs [(letter, score)…], return a
        corresponding string colored using ANSI codes.
        """
        output = ''
        for letter, score in scored_list:
            text_color = Code.BLACK_TEXT if not score else Code.WHITE_TEXT
            score_color = SCORE_COLORS[score]
            output += (f'{score_color}{Code.BOLD}{text_color} '
                       f'{letter.upper()} {Code.RESET} ')
        return output

    def show_menu(self):
        """Print menu prompt and return user's menu choice."""
        options = {
            'n': MenuOption.NEW_GAME,
            's': MenuOption.STATS,
            'e': MenuOption.EXIT
        }
        key = input('[N]ew game, [S]tats, [E]xit: ').lower()
        return options.get(key, None)

    def get_input(self, turn: int):
        """Return input during game round (ie a guess)."""
        return input(f'Round {turn}: ').lower()

    def update(self, game_state):
        """Print game state to screen. Called from model (Observer pattern)."""

        # if there's an error, just print that
        if isinstance(game_state.alert, Error):
            print(game_state.alert)
        else:  # else print whole game board
            self.draw_guesses(game_state)
            self.draw_alert(game_state.alert)
            self.draw_qwerty(game_state.qwerty)

    def draw_guesses(self, game_state):
        """
        Print guesses board. Previous guesses, then blank rows to a total of 6.
        """
        blank_row = [(' ', -1)] * 5  # -1 == LIGHT_GREY
        blank_rows_needed = game_state.MAX_TURNS - len(game_state.previous_guesses)
        blank_rows = [blank_row] * blank_rows_needed
        rows = game_state.previous_guesses + blank_rows

        print('\n')
        for row in rows:
            print(self.center(self.colorize(row)))
            print()

    def draw_alert(self, alert):
        """Print an alert box with game message or blank line if none."""
        alert = self.center(f'{Code.RED} {alert} {Code.RESET}') if alert else ''
        print(alert)

    def draw_qwerty(self, qwerty: list):
        """Print the qwerty layout letter tracker."""
        print()
        for i, row in enumerate(qwerty):
            print(self.center(self.colorize(row)))
            print()

    def draw_stats(self, stats: dict):
        """
        Print stats based on previous game scores. The labels of the 4 stats
        displayed in columns are dynamically padded to provide a flexible
        layout for changing values. (NB In theory, will break if
        `current_streak` (has the longest label) exceeds 3 digits.)
        """

        LEFT_COL = 15
        RIGHT_COL = 21
        PADDING = 4  # the 4 spaces between LABEL_STYLE and RESET below
        LABEL_STYLE = f'{Code.GREY}{Code.BLACK_TEXT}'
        VALUE_STYLE = f'{Code.DARK_GREY}{Code.BOLD}{Code.WHITE_TEXT}'
        COL_SPACE = '  '
        LINE_SPACE = '\n\n'

        def style_stat(stat: tuple, col_width: int):
            """
            Pad label given col and value width, wrap label and value in
            ANSI-coded styling.
            """
            label, value = stat
            spaces = col_width - PADDING - len(str(value))
            label = label.ljust(spaces)
            end = COL_SPACE if col_width == LEFT_COL else LINE_SPACE

            return f' {LABEL_STYLE} {label} {VALUE_STYLE} {value} {Code.RESET}{end}'

        print(
            LINE_SPACE,
            style_stat(stats['played'], LEFT_COL),
            style_stat(stats['current_streak'], RIGHT_COL),
            style_stat(stats['wins'], LEFT_COL),
            style_stat(stats['max_streak'], RIGHT_COL),
            f' Guess distribution: {LINE_SPACE}',
            self.histo(stats['distribution'], stats['last']),
            sep=''
        )

    def histo(self, totals: dict, last: int):
        """Turn game_state.stats distribution into a histogram."""

        MAX_SIZE = APP_WIDTH - 8
        output = ''

        # extract biggest value (ie most common score) upfront (other bars sized
        # proportionally to it). Provide a default in case there's no non-zero
        # score yet (`max([])` causes error).
        biggest = max([v for k, v in totals.items() if v > 0], default=1)

        # Draw each value as a bar sized relative to largest
        for k, v in totals.items():
            # latest score highlighted in green
            score_color = Code.GREEN if k == last else Code.DARK_GREY
            spaces = ' ' * round(MAX_SIZE * (v / biggest))  # size the bar
            output += (f' {k} {score_color}{spaces}{Code.WHITE_TEXT} {v} '
                       f'{Code.RESET}\n')
        return output

from curdle.config import AnsiCode as Code, SCORE_COLORS, Error, MenuOption


class View:
    def __init__(self, model):

        # Observer pattern: model will call update() when state changed
        model.attach(self)

    def colorize(self, scored_list: list):
        """expect a list of tuple pairs [(letter, score)…], return color version."""
        output = ''
        for letter, score in scored_list:
            text_color = Code.BLACK_TEXT if not score else Code.WHITE_TEXT
            score_color = SCORE_COLORS[score]
            output += (f'{score_color}{Code.BOLD}{text_color} '
                       f'{letter.upper()} {Code.RESET} ')
        return output

    def menu(self):
        prompt = []
        options = {}
        for option in MenuOption:
            label = str(option)
            options[label[0].lower()] = option
            prompt.append(f'[{label[0]}]{label[1:].lower()}')
        prompt = ", ".join(prompt)
        key = input(f'{prompt}: ').lower()
        return options.get(key, None)

    def get_input(self, turn):
        return input(f'Round {turn}: ').lower()

    def update(self, game_state):

        # if error
        if isinstance(game_state.alert, Error):
            print(game_state.alert)
        else:
            self.draw_guesses(game_state)
            self.draw_alert(str(game_state.alert))
            self.draw_qwerty(game_state.qwerty)

    def draw_guesses(self, game_state):
        blank_row = [(' ', -1)] * 5  # -1 == LIGHT_GREY
        blank_rows_needed = game_state.MAX_TURNS - len(game_state.previous_guesses)
        blank_rows = [blank_row] * blank_rows_needed
        rows = game_state.previous_guesses + blank_rows

        print('\n')
        for row in rows:
            print('          ', self.colorize(row))
            print()

    def draw_alert(self, alert):
        if alert:
            spaces = (38 // 2 - len(alert) // 2) * ' '
            alert = f'{spaces}{Code.RED} {alert} {Code.RESET}'
        else:
            alert = ''
        print(alert)

    def draw_qwerty(self, qwerty):
        print()
        for i, row in enumerate(qwerty):
            spaces = ('', '  ', '      ')
            print(spaces[i], self.colorize(row))
            print()

    def stats(self, stats: dict):
        label_style = f'{Code.GREY}{Code.BLACK_TEXT}'
        value_style = f'{Code.DARK_GREY}{Code.BOLD}{Code.WHITE_TEXT}'

        print(
            '\n\n'
            f' {label_style} Played      '
            f'{value_style} {stats["played"]} {Code.RESET}    '
            f'{label_style} Current streak '
            f'{value_style} {stats["current"]} {Code.RESET}\n\n'
            f' {label_style} Win %     '
            f'{value_style} {stats["wins"]} {Code.RESET}   '
            f' {label_style} Max streak     '
            f'{value_style} {stats["max"]} {Code.RESET}\n\n'
            ' Guess distribution: \n\n'
            f'{self.histo(stats["distribution"], stats["last"])}'
        )

    def histo(self, totals: dict, last: int):
        """Turn game_state.stats distribution into a histogram."""

        MAX_SIZE = 34
        output = ''

        # extract biggest value (ie most common score) upfront (other bars sized
        # proportionally to it). Provide a default in case there's no non-zero
        # score yet (`max([])` causes error).
        biggest = max([v for k, v in totals.items() if k > 0], default=1)

        # Draw each value as a bar sized relative to largest
        for k, v in totals.items():
            # latest score highlighted in green
            score_color = Code.GREEN if k == last else Code.DARK_GREY
            spaces = ' ' * round(MAX_SIZE * (v / biggest))  # size the bar
            output += (f' {k} {score_color}{spaces}{Code.WHITE_TEXT} {v} '
                       f'{Code.RESET}\n')
        return output

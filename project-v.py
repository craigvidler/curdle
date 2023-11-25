from curdle.model import Wordle
from vanilla.view import View
import sys


def main():
    # Pass in answer if required during dev
    answer = sys.argv[1] if len(sys.argv) > 1 else ''
    view = View()
    wordle = Wordle(answer)  # game object/model
    wordle.new_game()
    wordle.submit()
    view.draw(wordle)


if __name__ == '__main__':
    main()

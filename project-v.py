from curdle.model import Wordle
from vanilla.view import View
import sys


def main():
    # Pass in answer if required during dev
    answer = sys.argv[1] if len(sys.argv) > 1 else ''
    wordle = Wordle(answer)  # game object/model
    view = View(wordle)  # pass in wordle (model) to make observer link

    wordle.new_game()
    wordle.submit('slate')
    wordle.submit('yetis')


if __name__ == '__main__':
    main()

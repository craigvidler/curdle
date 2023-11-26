from curdle.model import Wordle
from vanilla.controller import Controller
from vanilla.view import View
import sys


def main():
    # Pass in answer if required during dev
    answer = sys.argv[1] if len(sys.argv) > 1 else ''
    wordle = Wordle(answer)  # game object/model
    view = View(wordle)  # pass in wordle (model) to make observer link
    controller = Controller(wordle, view)
    controller.run()


if __name__ == '__main__':
    main()

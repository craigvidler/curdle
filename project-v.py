from curdle.controller import Controller
from curdle.model import Wordle
from curdle.view import View
import curses
import sys


def main(stdscr):
    # Pass in answer if required during dev
    answer = sys.argv[1] if len(sys.argv) > 1 else ''
    wordle = Wordle(answer)  # game object/model
    view = View(curses, stdscr)
    Controller(view, wordle).run()


curses.wrapper(main)

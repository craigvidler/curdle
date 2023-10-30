Wordle
==============================================================================

A clone of Wordle by Josh Wardle (https://www.nytimes.com/games/wordle/), as a terminal/command line game in Python.

The Wordle class in wordle.py models the core game logic of Wordle. User input and display are left to a front end (the client code using this class). 

Unlike official Wordle, this will support indefinite multiple games in one
session, but it's otherwise similar.

Author: Craig Vidler, 30 Oct 23



## APPLICATION LOGIC (wordle.py)
------------------------------------------------------------------------------

+   ### Interface

    Instantiate, specify wordlists if required (`wordle = Wordle()`, `wordle = Wordle(answers_file='', guesses_file=''`)). See below for expected content/format of wordlists. Call `wordle.new_game()` to start. 

    Call `wordle.submit(guess)`; if `guess` is a valid guess, it's returned as a list of tuples with a score for each letter eg `[('s', 1), ('c', 1), ('o', 3), ('r', 2), ('e', 1)]`. 

    The letter tracker (a dict not list of scored letter tuples as above) is updated with each valid guess and is available at `wordle.letter_tracker` for display. 

    `wordle.round` tracks the current round; when it equals `wordle.max_round`, the game is over/lost. Every round, the client code can check whether `guess` equals `wordle.answer`; if so, the game is won.


+   ### Wordlists

    The word lists are those from Josh Wardle's original pre-NYT game. Source:

    https://gist.github.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b
    (2315 answers only)
    https://gist.github.com/cfreshman/cdcdf777450c5b5301e439061d29694c
    (10657 valid guesses excluding the answers)

    For ease of use, I've joined the two into one inclusive list of 12972
    valid guesses and valid answers (valid answers being also valid guesses),
    and kept one list of just the 2315 valid answers. Other wordlists if used would have to adhere to this pattern.


+   ### Guess scoring

    There are four status codes for letters in scored guesses and in the
    letter tracker:

    * 0 (unguessed/light grey)
    * 1 (guessed/dark grey)
    * 2 (present/yellow)
    * 3 (located/green)

    0 applies in the letter tracker only.


+   ### Core logic

    Contained in the submit method, this takes an attempted guess and if it's
    not valid, returns `None`; if a valid guess, it will return a marked-up,
    numerically scored version of the word, leaving the display details to
    the client code.

    It's a little tricky to cover all various possible combinations of
    duplicate and non-duplicate letters and get the scoring right. There are
    quite a few articles, Youtube videos and Github repos of Wordle clones
    which use a lazy approach and get it wrong. The procedure here
    (two-pass, status 3/green then status 2/yellow, deletions from answer) is
    one solution; there might be a nicer way, but this works.

    Procedure: `scored_guess` can't use a dict since duplicate letters in a
    guess would cause duplicate keys, so it's a list of tuples. We need to
    copy `answer` to a list so we can delete letters as we go to avoid
    counting dupes. First find any present and well-located letters
    (ie green). Mark these as status 3 in `scored_guess` and remove from
    `answer_letters`. Then (ignoring letters already marked status 3), find
    present but not well-located letters (ie yellow). Mark them status 2 in
    `scored_guess` and remove from `answer_letters`.


+   ### Letter tracker

    This corresponds to the keyboard at the bottom of the interface in
    official Wordle, and shows those letters the user has already guessed.
    There's a ratchet effect whereby a letter will always show the highest
    status it's reached, so that eg if a given letter has been guessed and is
    already 3/well-located/green, it will not be displayed as 1/dark
    grey/guessed or 2/present/yellow thereafter.

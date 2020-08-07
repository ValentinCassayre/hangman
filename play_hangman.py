from hangman import select_mode
from random import choice


play = True

while play:

    game = None
    game_name = None
    raw_input = None

    mode = None
    word_answer = None
    player_word = None
    tested_letters = None
    wrong_letters = None
    tested_words = None
    trials = 0
    lives = 6
    unknown = '_'
    shuffle_bol = True

    while game is None:

        raw_input = input(f'Choose a game mode :').lower()

        game = select_mode(raw_string=raw_input)

    if not game:
        play = False

    else:
        game.start()

        while game.started:
            game.display(player_word=True, wrong_letters=True, lives=False, trials=True, game_mode=True,
                         ascii_pic=True, log=True, console_print=True)

            inp = input('Guess a letter or the word :')

            if game.input(inp):
                game.proceed()

        game.display(player_word=True, wrong_letters=True, lives=False, trials=True, game_mode=True,
                     ascii_pic=True, log=True, console_print=True)

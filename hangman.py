from random import randint, choice, shuffle
from collections import Counter

from display import cls
from ascii_hangman import ASCII_HANGMAN, ASCII_HANGMAN_DISCORD, ASCII_HANGMAN_TWITTER
from words import WORDS, ALPHABET


class Hangman:
    def __init__(self, word_answer=None, player_word=None, tested_letters=None, wrong_letters=None, tested_words=None,
                 trials=0, lives=6, unknown='_', shuffle_bol=True):

        self.started = False
        self.ended = False
        self.update = False
        self.word_list = WORDS
        self.mode = 'classic'
        self.shuffle = shuffle_bol

        self.word_answer = word_answer
        self.possible_answers = None

        if tested_letters is None:
            tested_letters = []
        if wrong_letters is None:
            wrong_letters = []
        if tested_words is None:
            tested_words = []

        self.tested_letters = tested_letters
        self.wrong_letters = wrong_letters
        self.tested_words = tested_words

        self.unknown = unknown

        self.player_word = player_word

        self.letter_inp = None
        self.word_inp = None
        self.good_inp = False
        self.success = False

        self.log = None

        self.trials = trials
        if lives > len(ASCII_HANGMAN):
            lives = 6
        self.lives = lives

    def start(self):
        self.started = True
        self.update = True

        index = randint(0, len(self.word_list))
        self.word_answer = self.word_list[index]
        self.possible_answers = [self.word_answer]

        self.player_word = list(self.unknown * len(self.word_answer))

    def stop(self):
        self.started = False
        self.ended = True
        self.update = True

    def input(self, inp):
        good_inp = True
        self.letter_inp = None
        self.word_inp = None

        for letter in inp:
            if letter.lower() not in ALPHABET:
                good_inp = False
                self.log = f'"{inp}" is not a valid letter or word, it contains "{letter}".'

        if len(inp) == 1:
            if inp in self.tested_letters:
                good_inp = False
                self.log = f'letter "{inp}" has already been used.'
            if good_inp:
                self.letter_inp = inp

        elif len(inp) > 1:
            if good_inp:
                self.word_inp = inp

        else:
            good_inp = False
            if self.log is None:
                self.log = f'"{inp}" is not a valid letter or word, it is too small.'

        return good_inp

    def proceed(self):
        if self.letter_inp is not None:
            self.check_letter()

        if self.word_inp is not None:
            self.check_word()

        if self.shuffle:
            shuffle(self.wrong_letters)

        with open('possible_answers.txt', 'w') as log:
            log.write('\n'.join(self.possible_answers))

        self.check_end()

    def fail(self):
        self.lives -= 1
        self.wrong_letters.append(self.letter_inp)

    def check_letter(self):
        self.success = False
        self.update = True

        self.tested_letters.append(self.letter_inp)
        self.trials += 1
        for i, letter in enumerate(self.word_answer.lower()):
            if letter == self.letter_inp:
                self.player_word[i] = self.word_answer[i]
                self.success = True

        if not self.success:
            self.fail()

    def check_word(self):
        if self.word_answer.lower() == self.word_inp.lower():
            self.player_word = list(self.word_answer)
            self.update = True

        self.tested_words.append(self.word_answer)

    def check_end(self):
        if self.lives <= 0:
            self.log = f'Game over! The word was {self.word_answer}'
            self.stop()
        elif self.unknown not in self.player_word:
            self.log = f'Good game ! You successfully guessed the word {self.word_answer}'
            self.stop()

    def display(self, player_word=False, wrong_letters=False, lives=False, trials=False, game_mode=False,
                ascii_pic=False, log=False, console_print=False, discord_form=False, twitter_form=False):
        self.update = False

        to_write = []
        if player_word:
            temp = f' {" ".join(self.player_word)}'
            if discord_form:
                temp = f'``{temp}``'
            to_write.append(temp)
        if wrong_letters:
            to_write.append(f' Wrong guesses : {" - ".join(self.wrong_letters)}')
        if lives:
            to_write.append(f' Lives : {self.lives}')
        if trials:
            to_write.append(f' Trial : {self.trials}')
        if game_mode:
            to_write.append(f' Game type : {self.mode}')
        if ascii_pic:
            temp = ASCII_HANGMAN[self.lives]
            if discord_form:
                temp = ASCII_HANGMAN_DISCORD[self.lives]
            if twitter_form:
                temp = ASCII_HANGMAN_TWITTER[self.lives]
            to_write.append(temp)
        if self.log is not None:
            if log:
                to_write.append(f'{self.log}')
            self.log = None

        string = '\n'.join(to_write)

        if console_print:
            cls()
            print(string)

        return string

    def export_dict(self):
        data = {'game_mode': self.mode,  'word_answer': self.word_answer, 'player_word': self.player_word,
                'tested_letters': self.tested_letters, 'wrong_letters': self.wrong_letters,
                'trials': self.trials, 'lives': self.lives}
        return data


class HardcoreHangman(Hangman):
    def __init__(self, word_answer=None, player_word=None, tested_letters=None, wrong_letters=None, tested_words=None,
                 trials=0, lives=6, unknown='_', shuffle_bol=True):
        super().__init__(word_answer, player_word, tested_letters, wrong_letters, tested_words, trials, lives, unknown,
                         shuffle_bol)
        self.mode = 'hardcore'

    def start(self):
        self.started = True
        self.update = True

        self.create_possible_answers(choose_word=True)

    def create_possible_answers(self, from_word_list=True, from_number=False, choose_word=False):
        if from_word_list:
            self.possible_answers = self.word_list
        if choose_word:
            self.word_answer = choice(self.possible_answers)
            length = len(self.word_answer)
            self.player_word = list(self.unknown * length)
            self.remove_wrong_length()
        if from_number:
            new_list = []
            for n in range(from_number):
                new_list.append(choice(self.possible_answers))

            self.possible_answers = new_list
            self.remove_duplicates()

    def shaping(self, word, letters_searching):
        new_word = ''
        for letter in word:
            for letter_searching in letters_searching:
                if letter.lower() == letter_searching.lower():
                    new_word += letter
                    break
            else:
                new_word += self.unknown

        return new_word

    def remove_duplicates(self):
        self.possible_answers = list(dict.fromkeys(self.possible_answers))

    def remove_wrong_length(self):
        self.possible_answers = [word for word in self.possible_answers if len(word) == len(self.player_word)]

    def remove_wrong_letters(self):
        for wrong_letter in self.wrong_letters:
            self.possible_answers = [word for word in self.possible_answers if wrong_letter not in word]

    def remove_wrong_shaping(self):
        self.possible_answers = [word for word in self.possible_answers
                                 if
                                 self.shaping(word, self.tested_letters).lower() == ''.join(self.player_word).lower()]

    def calc(self, create_possible_answers=True, wrong_letters=True, length=True, player_word=True):
        if create_possible_answers:
            self.create_possible_answers()
        if wrong_letters:
            self.remove_wrong_letters()
        if length:
            self.remove_wrong_length()
        if player_word:
            self.remove_wrong_shaping()

    def check_letter(self):
        self.success = False
        self.update = True

        self.tested_letters.append(self.letter_inp)
        self.trials += 1

        best_forms = Counter([self.shaping(word, self.letter_inp) for word in self.possible_answers]).most_common()
        form = best_forms[0][0]
        self.possible_answers = [word for word in self.possible_answers if self.shaping(word, self.letter_inp) == form]

        for i, letter in enumerate(form):
            if letter != self.unknown:
                self.player_word[i] = letter
                self.success = True

        if not self.success:
            self.fail()

        self.word_answer = choice(self.possible_answers)

    def check_word(self):
        new_list = [word for word in self.possible_answers if word.lower() != self.word_inp.lower()]

        if len(new_list) == 0:
            self.player_word = choice(self.possible_answers)
            self.update = True

        if len(new_list) != len(self.possible_answers):
            self.possible_answers = new_list
            self.tested_words.append(self.word_answer)


def select_mode(mode=None, word_answer=None, player_word=None, tested_letters=None, wrong_letters=None, tested_words=None,
                trials=0, lives=6, unknown='_', shuffle_bol=True, raw_string=None):

    exit_names = ['exit', 'l', 'leave']
    game_modes = ['classic', 'hardcore']

    if raw_string is not None:
        commands = raw_string.split(' ')
        for parameter in commands:
            if '=' in parameter:
                sp = parameter.split('=')
                if sp[0] == 'mode':
                    mode = sp[1]
                elif sp[0] == 'word_answer':
                    word_answer = sp[1]
                elif sp[0] == 'player_word':
                    player_word = list(sp[1])
                elif sp[0] == 'tested_letters':
                    tested_letters = list(sp[1])
                elif sp[0] == 'wrong_letters':
                    wrong_letters = list(sp[1])
                elif sp[0] == 'tested_words':
                    tested_words = sp[1].split(',')
                elif sp[0] == 'trials':
                    trials = int(sp[1])
                elif sp[0] == 'lives':
                    lives = int(sp[1])
                elif sp[0] == 'unknown':
                    unknown = sp[1]
                elif sp[0] == 'shuffle_bol':
                    shuffle_bol = bool(sp[1])
            elif parameter in exit_names:
                return False
            elif parameter in game_modes:
                mode = parameter

    if mode == 'classic':
        game = Hangman(word_answer, player_word, tested_letters, wrong_letters, tested_words, trials, lives,
                       unknown, shuffle_bol)
    else:
        game = HardcoreHangman(word_answer, player_word, tested_letters, wrong_letters, tested_words, trials, lives,
                               unknown, shuffle_bol)
    return game

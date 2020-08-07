import tweepy
import time
import pandas as pd

import json
from key import keys

from hangman import select_mode


class TwitterBot:
    def __init__(self):
        self.api = self.create_api()

        with open('twitter.json', 'r') as settings:
            self.settings = json.load(settings)

        self.options = ['hangman']
        self.username = '@HardcoreHangman'
        self.bot_id = 1289271747125170177
        self.content = None
        self.tweet = None
        self.reply = None
        self.id = None
        self.string = None

        try:
            self.df = pd.read_pickle('data.pk')
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=['user_id', 'tweet_id',
                                            'game_mode', 'word_answer', 'player_word', 'tested_letters',
                                            'wrong_letters', 'trials', 'lives'])
            self.df.set_index('user_id', inplace=True)

    @staticmethod
    def create_api():
        auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
        auth.set_access_token(keys['access_token'], keys['access_token_secret'])
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        try:
            api.verify_credentials()
        except tweepy.error.TweepError as e:
            print(f'API Error : {e}')
        print('API created')
        return api

    def check_mentions(self):
        print(f'Checking mentions')

        for self.tweet in tweepy.Cursor(self.api.mentions_timeline, since_id=self.settings['since_id']).items():

            if self.tweet.user.id == self.bot_id:  # go to next tweet if the quote is from himself
                continue

            print(f"Answering to {self.tweet.user.name}")
            print(self.tweet.text)

            try:
                self.id = self.tweet.user.id

                self.settings['since_id'] = max(self.tweet.id, self.settings['since_id'])

                self.content = self.tweet.text.lower().replace(f'{self.username} ', '')

                if self.content.startswith('/'):
                    pass

                if self.tweet.in_reply_to_status_id is not None:  # this is a reply

                    try:
                        if self.tweet.in_reply_to_status_id == self.df.loc[self.id, 'reply_id']:
                            self.game_continue()
                        else:
                            self.string = f"Hey {self.tweet.user.screen_name} ! " \
                                          f"Tweet and quote {self.username} to start a new game or " \
                                          f"continue your game by replying here : " \
                                          f"https://twitter.com/Pyfinity_/status/" \
                                          f"{self.df.loc[self.id, 'reply_id']}."
                    except KeyError:
                        self.string = f"Hey @{self.tweet.user.screen_name} ! " \
                                      f"Tweet and quote {self.username} to start your first game."

                else:  # this is a tweet
                    self.game_start()

                try:
                    self.reply = self.api.update_status(
                        status=self.string,
                        in_reply_to_status_id=self.tweet.id,
                        auto_populate_reply_metadata=True
                    )  # pic media_ids=[self.api.media_upload("test.png").media_id]
                    print(f"Answered to {self.tweet.user.name}")

                except tweepy.error.TweepError as error:
                    print(f'Error while tweeting to {self.tweet.user.name} : {error}')

            except IndexError as error:
                print(f'Error while analysing tweet from {self.tweet.user.name} : {error}')

            try:
                self.df.loc[self.id, 'tweet_id'] = int(self.tweet.id)
                self.df.loc[self.id, 'reply_id'] = int(self.reply.id)
                self.df.loc[self.id, 'last_modification'] = self.id

            except KeyError as error:
                print(f'Error while saving tweet from {self.tweet.user.name} : {error}')

            # if any(option in tweet.text.lower() for option in self.options):
            #     pass

            # if not tweet.user.following:
            #    tweet.user.follow()

        self.update_settings()
        self.update_data()

    def game_start(self):

        game = select_mode(raw_string=self.content)

        game.start()
        self.game_save(game)
        self.game_end_round(game)

    def game_continue(self):

        game = self.game_load()

        game.calc(create_possible_answers=True, wrong_letters=True, player_word=True)
        game.input(self.content)
        game.proceed()
        self.game_end_round(game)

    def game_end_round(self, game):
        self.string = game.display(player_word=True, wrong_letters=True, lives=True, trials=True, game_mode=True,
                                   ascii_pic=True, log=True, twitter_form=True)

        if len(self.string) > 240:
            self.string = game.display(player_word=True, wrong_letters=True, lives=True, trials=True, game_mode=True,
                                       ascii_pic=False, log=True, twitter_form=True)
        self.game_save(game)

    def game_load(self):
        game_mode = self.df.loc[self.id, 'game_mode']
        word_answer = self.df.loc[self.id, 'word_answer']
        player_word = list(self.df.loc[self.id, 'player_word'])
        tested_letters = list(self.df.loc[self.id, 'tested_letters'])
        wrong_letters = list(self.df.loc[self.id, 'wrong_letters'])
        tested_words = list(self.df.loc[self.id, 'tested_words'])
        trials = self.df.loc[self.id, 'trials']
        lives = self.df.loc[self.id, 'lives']

        game = select_mode(game_mode, word_answer, player_word, tested_letters, wrong_letters, tested_words,
                           trials, lives)

        return game

    def game_save(self, game):
        self.df.loc[self.id, 'game_mode'] = game.mode
        self.df.loc[self.id, 'word_answer'] = game.word_answer
        self.df.loc[self.id, 'player_word'] = ''.join(game.player_word)
        self.df.loc[self.id, 'tested_letters'] = ''.join(game.tested_letters)
        self.df.loc[self.id, 'wrong_letters'] = ''.join(game.wrong_letters)
        self.df.loc[self.id, 'tested_words'] = ''.join(game.tested_words)
        self.df.loc[self.id, 'trials'] = game.trials
        self.df.loc[self.id, 'lives'] = game.lives

    def update_settings(self):
        with open('twitter.json', 'w') as settings:
            json.dump(self.settings, settings)

    def update_data(self):
        self.df.to_pickle('data.pk')
        self.df.to_csv('data.csv', sep=';')

    def delete_replies(self):
        print('DELETING ALL REPLIES')
        for tweet in tweepy.Cursor(self.api.user_timeline).items():
            if tweet.in_reply_to_status_id is not None:
                try:
                    self.api.destroy_status(tweet.id)
                except tweepy.error.TweepError:
                    pass


def main():
    bot = TwitterBot()

    while True:
        bot.check_mentions()
        print('Waiting...')
        time.sleep(15)


if __name__ == "__main__":
    main()

import discord

from hangman import select_mode

client = discord.Client()
token = 'NzI3NDI0NzA0Nzc5OTExMTc5.Xvrprw.P_IQrSZWRJXV0YdQuLgwxQ3M87I'
admin_name = 'Pyfinity'

game = None


@client.event
async def on_message(message):
    await client.wait_until_ready()
    global game

    if message.author.id == 727424704779911179:
        return

    if message.author.name == admin_name:

        if message.content.startswith('!l'):
            await message.channel.send('Logging out!')
            print(f'{message.author.name} is logging out the bot.')
            await client.logout()

    if message.content.startswith('!hangman'):

        game = select_mode(raw_string=message.content.replace('!hangman ', ''), unknown='◯')

        if not game:
            return

    elif 'hangman' in message.content:
        await message.channel.send(f'Type "!hangman" to start an hangman game.')

    if game is not None and not game.ended:
        if game.started:
            if game.input(message.content):
                game.proceed()
            else:  # not a valid input, to avoid spam bot will not respond
                game.update = False
        else:
            game.start()
            game.success = True

        if game.update:

            embed = discord.Embed()

            if game.success:
                embed.colour = discord.Colour.green()
            else:
                embed.colour = discord.Colour.red()

            embed.title = f'Hangman started ({game.mode})'

            string = game.display(
                player_word=True, wrong_letters=True, trials=True, ascii_pic=True, log=True, discord_form=True)

            embed.description = f'{string}'

            await message.channel.send(embed=embed)

        else:
            game.display()


client.run(token)

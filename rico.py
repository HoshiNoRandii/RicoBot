### RicoBot ###

# imports for the .env to work
from os import environ
from dotenv import load_dotenv

# so that we can use the Discord API
import discord

# loading in the token
load_dotenv()
token = environ['TOKEN']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Rico is ready!')


@client.event
async def on_message(message):
    # don't have Rico reply to himself
    if message.author == client.user:
        return


    # respond to messages starting with 'r!'
    if message.content.startswith('r!'):
        # split the messgage into individual words
        splitMessage = message.content.split()


        # no command: send '?'
        if len(splitMessage) < 2:
            await message.channel.send('?')
            return


        # grab the command
        command = splitMessage[1]


        # nick: change the nickname of the mentioned people
        # syntax: r! nick @user1 @user2 ... [desired nickname]
        # NOTE: only works on correct syntax
        # still need to implement error messages for incorrect syntax
        if command == 'nick':
            # grab the nickname
            # find where in the message the nickname starts
            nnameIndex = 2
            while(splitMessage[nnameIndex].startswith('<@')):
                nnameIndex +=1
            # slice off the nickname
            nnameList = splitMessage[nnameIndex:]
            # make it one string again
            nname = ' '.join(nnameList)

            # give the nickname to every mentioned user
            for friend in message.mentions:
                await friend.edit(nick = nname)
            return


        # hi: send 'henlo!'
        if command == 'hi':
            await message.channel.send('henlo!')
            return


        # other command: send '?'
        else:
            await message.channel.send('?')
            return

client.run(token)

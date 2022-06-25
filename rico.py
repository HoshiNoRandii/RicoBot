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

        # if no command, respond with '?'
        if len(splitMessage) < 2:
            await message.channel.send('?')
            return

        # grab the command
        command = splitMessage[1]

        # respond 'henlo!' to the command 'hi'
        if command == 'hi':
            await message.channel.send('henlo!')
            return

        # respond '?' to anything else
        else:
            await message.channel.send('?')
            return

client.run(token)

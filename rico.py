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
    if message.auther == client.user:
        return

    # respond to messages starting with 'r!'
    if message.content.startswith('r!'):
        await message.channel.send('henlo!'):

client.run(token)

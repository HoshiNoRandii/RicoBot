###############################################################################
#
# RicoBot
# by HoshiNoRandii
#
# I wrote this bot so that my friends could all change each other's
# nicknames in our server!
# 
###############################################################################

import asyncio

# imports for the .env to work
from os import environ
from dotenv import load_dotenv

# so that we can use the Discord API
import discord
from discord.ext import commands

# loading in the token
load_dotenv()
token = environ['TOKEN']

# making sure to have all necessary permissions
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(intents = intents, command_prefix = ('r! ','r!'))


# load in the cogs
async def loadCogs():
    cogsList = ['commands']
    for cog in cogsList:
        await bot.load_extension(cog)


@bot.event
async def on_ready():
    print('Rico is ready!')


@bot.event
async def on_message(message):
    # don't have Rico reply to himself
    if message.author == bot.user:
        return
    
    # so that commands work as well as anything in here
    await bot.process_commands(message)
    
    return

async def main():
    async with bot:
        await loadCogs()
        await bot.start(token)

asyncio.run(main())

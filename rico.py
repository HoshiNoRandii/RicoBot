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

# so that we can connect to the postgres server
import connect

# set to True for [BETA] RicoBot
BETA = True

# loading in the token
load_dotenv()
if BETA == True:
    token = environ["BETA_TOKEN"]
else:
    token = environ["TOKEN"]

# making sure to have all necessary permissions
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(intents=intents, command_prefix=("r! ", "r!", "R! ", "R!"))
# remove default help command so the custom one works
bot.remove_command("help")

# create the connection pool for the postgres server
connect.init()


# load in the cogs
async def loadCogs():
    cogsList = ["names", "other_cmds", "dev_tools"]
    for cog in cogsList:
        await bot.load_extension(cog)
        print(f"{cog} cog loaded")


@bot.event
async def on_ready():
    playing = discord.Game(name="r! help")
    await bot.change_presence(activity=playing)
    print("Rico is ready!")


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

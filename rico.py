###############################################################################
#
# RicoBot
# by HoshiNoRandii
#
# I wrote this bot so that my friends could all change each other's
# nicknames in our server!
# 
###############################################################################

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

bot = commands.Bot(intents = intents, command_prefix = 'r! ')



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


### Commands ###

# nick: change the nickname of the mentioned people
# syntax: r! nick @user1 @user2 ... [nickname]
# NOTE: only works on correct syntax
# still need to implement error messages for incorrect syntax
@bot.command()
async def nick(ctx, *args):
    # grab the nickname
    # find where in the message the nickname starts
    # uses the fact that mentions start with '<' and end with '>'
    # so the first word in the nickname can't be in angle brackets
    nnameIndex = 0
    while args[nnameIndex].startswith('<') and args[nnameIndex].endswith('>'):  
        nnameIndex +=1
    # slice off the nickname
    nnameList = args[nnameIndex:]
    # make it one string again
    nname = ' '.join(nnameList)

    # give the nickname to every mentioned user
    for friend in ctx.message.mentions:
        await friend.edit(nick = nname)
    return


# hi: send 'henlo!'
@bot.command()
async def hi(ctx):
    await ctx.channel.send('henlo!')
    return

bot.run(token)

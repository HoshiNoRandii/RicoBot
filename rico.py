# RicoBot

import discord

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

client.run('')

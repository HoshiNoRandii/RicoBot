### Commands ###
# a cog containing all of RicoBot's commands

# so that we can use the Discord API
import discord
from discord.ext import commands


class CommandsCog(commands.Cog, name = 'Commands'):

    def __init__(self, bot):
        self.bot = bot

    # nick: change the nickname of the mentioned people
    # syntax: r! nick @user1 @user2 ... [nickname]
    # NOTE: only works on correct syntax
    # still need to implement error messages for incorrect syntax
    @commands.command(brief = 'Set users nicknames',\
            help = 'Type ```r! nick @user1 @user2 @user3 [nickname]```\
            to change the nicknames of every mentioned user to [nickname].\
            You can include as many people as you want in the same command.\n\
            Will not work if the first word in the nickname is enclosed in\
            <angle brackets>.')
    async def nick(self, ctx, *args):
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
            if friend == ctx.guild.owner:
                await ctx.channel.send(\
                        '{} change your nickname!!'.format(friend.mention))
            else:
                await friend.edit(nick = nname)
        return


    # hi: send 'henlo!'
    @commands.command(brief = 'Say hi!',\
            help = 'Type ```r! hi``` to say hi to RicoBot.')
    async def hi(self,ctx):
        await ctx.channel.send('henlo!')
        return


# necessary to link the cog to the main file
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))

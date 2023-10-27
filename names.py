### Names ###
# a cog containing RicoBot's naming-related commands

# so that we can use the Discord API
import discord
from discord.ext import commands

from other_cmds import syntaxError, isUserMent

# so that we can use the connection pool to connect
# to the postgres server
from connect import db_connector


class CommandsCog(commands.Cog, name="Names"):
    def __init__(self, bot):
        self.bot = bot

        ## nick: change the nickname of the mentioned people

    # syntax: r! nick @user1 @user2 ... [nickname]
    @commands.command(
        name="nick",
        aliases=["nickname", "Nick", "Nickname"],
        brief="set friends' nicknames",
        help="""Type `r! nick @user1 @user2 @user3 [nickname]` to change the nicknames of every mentioned user to [nickname]. You can include as many people as you want in the same command.\n
Character Limit: 32\n
Notes:
- Will not work if the first word in the nickname starts with `<@` and ends with `>`.
- RicoBot cannot change the nickname of the server owner. He instead will mention them again and ask them to change their name.""",
    )
    async def nick(self, ctx, *args):
        # check that there are at least 2 arguments
        # and that the first argument is a user mention
        if (len(args) < 2) or (not isUserMent(args[0])):
            await syntaxError(ctx)
            return

        # grab the nickname
        # find where in the message the nickname starts
        # uses the fact that user mentions start with '<@' and end with '>'
        # so the first word in the nickname can't follow this pattern.
        nnameIndex = 0
        while isUserMent(args[nnameIndex]):
            nnameIndex += 1
        # slice off the nickname
        nnameList = args[nnameIndex:]
        # make it one string again
        nname = " ".join(nnameList)
        # check that it isn't too long
        if len(nname) > 32:
            await ctx.channel.send("that nickname is too long! (max: 32 characters)")
            return

        # give the nickname to every mentioned user
        for friend in ctx.message.mentions:
            if friend == ctx.guild.owner:
                await ctx.channel.send(f"{friend.mention} change your nickname!!")
            else:
                await friend.edit(nick=nname)
        # announce that it's been changed
        await ctx.channel.send("nickname changed!")
        return


# necessary to link the cog to the main file
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
    return

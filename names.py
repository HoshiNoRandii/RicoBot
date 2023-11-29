### Names ###
# a cog containing RicoBot's naming-related commands

# so that we can use the Discord API
import discord
from discord.ext import commands

from other_cmds import syntaxError

# so that we can use the connection pool to connect
# to the postgres server
from connect import (
    db_connector_no_args,
    db_connector_with_args,
    dbGetName,
    dbGetPronouns,
    dbGetNameList,
    dbGetPronounList,
    dbUpdateName,
    dbUpdatePronouns,
    dbUpdateNickname,
)


class CommandsCog(commands.Cog, name="Names"):
    def __init__(self, bot):
        self.bot = bot

    ## nick: change the nickname of the mentioned people
    # syntax: r! nick @user1 @user2 ... [nickname]
    @commands.command(
        name="nick",
        aliases=["nickname", "Nick", "Nickname", "NickName", "nickName", "NICKNAME"],
        brief="set friends' nicknames",
        help="""Type `r! nick @user1 @user2 @user3 [nickname]` to change the nicknames of every mentioned user to [nickname]. You can include as many people as you want in the same command.\n
Character Limit: 32\n
Notes:
- Will not work if the first word in the nickname starts with `<@` and ends with `>`.
- RicoBot cannot change the nickname of the server owner. He instead will mention them again and ask them to change their name.""",
    )
    @db_connector_with_args
    async def nick(self, ctx, *args, cursor=None):
        try:
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
                await ctx.channel.send(
                    "that nickname is too long! (max: 32 characters)"
                )
                return

            # give the nickname to every mentioned user
            for friend in ctx.message.mentions:
                await updateNickname(ctx, friend, nname, cursor)

        except Exception as error:
            print(error)

        return

    ## setname: set your name
    # syntax: r! setname [name]
    @commands.command(
        name="setname",
        aliases=["setName", "Setname", "SetName", "SETNAME"],
        brief="set your name",
        help="""Type `r! setname [name]` to change your name to [name]. This will be the name people see when they use the `getname` command, and will also be listed as a role.\n
Character Limit: 32""",
    )
    @db_connector_with_args
    async def setName(self, ctx, *args, cursor=None):
        try:
            newName = " ".join(args)
            # check that name isn't too long
            if len(newName) > 32:
                await ctx.channel.send("that name is too long! (max: 32 characters)")
                return
            await updateNameRole(ctx.guild, ctx.author, cursor, newName)
            dbUpdateName(ctx.guild, ctx.author, cursor, newName)
            await ctx.channel.send("name set!")

        except Exception as error:
            print(error)

        return

    ## getname: get the name of a server member
    # syntax: r! getname [name]
    @commands.command(
        name="getname",
        aliases=["getName", "Getname", "GetName", "GETNAME"],
        brief="view friends' names",
        help="""Type `r! getname @user1 @user2 @user3` and I'll tell you the names of the users you mentioned. You can mention as many people as you like.""",
    )
    @db_connector_no_args
    async def getName(self, ctx, *, cursor=None):
        try:
            msg = ""
            for friend in ctx.message.mentions:
                # insert newline character if this is not the first friend
                if msg != "":
                    msg = msg + "\n"

                # get name from database
                name = dbGetName(ctx.guild, friend, cursor)

                # update msg
                msg = msg + f"{friend.name}"
                if friend.nick:
                    msg = msg + f" (aka {friend.nick})"
                msg = msg + f"'s name is {name}."

            if msg != "":  # guard against if no users were mentioned
                await ctx.channel.send(msg)

        except Exception as error:
            print(error)

        return

    ## make sure to update the db if somebody
    # makes manual changes to their nickname
    # before and after are instances of discord.Member
    @commands.Cog.listener("on_member_update")
    @db_connector_no_args
    async def manualNickUpdate(self, before, after, *, cursor=None):
        try:
            # if nickname changed
            if before.nick != after.nick:
                dbUpdateNickname(after.guild, after, cursor)

        except Exception as error:
            print(error)

        return

    ## make sure to update the db if somebody
    # makes manual changes to their name role
    # before and after are instances of discord.Role
    @commands.Cog.listener("on_guild_role_update")
    @db_connector_no_args
    async def manualNameUpdate(self, before, after, *, cursor=None):
        try:
            server = before.guild

            # manual name role update
            if isNameRole(before, server, cursor):
                for member in after.members:
                    dbUpdateName(server, member, cursor, after.name)

        except Exception as error:
            print(error)

        return


## helper functions ##


## isUserMent(word): str -> bool
# returns True if word is a user mention
# uses the fact that user mentions begin with <@ and end with >
# assumes that word does not contain any whitespace
def isUserMent(word):
    return word.startswith("<@") and word.endswith(">")


# updates a user's nickname in the server
# and in the user_list table
# ctx argument is an instance of discord.ext.commands.Context
# member argument is an instance of discord.Member
async def updateNickname(ctx, member, newNick, cursor):
    if member == ctx.guild.owner:
        await ctx.channel.send(f"{member.mention} change your nickname!!")
    else:
        await member.edit(nick=newNick)
        dbUpdateNickname(ctx.guild, member, cursor)
        # announce that it's been changed
        await ctx.channel.send("nickname changed!")
    return


# updates a user's name role
# server argument is an instance of discord.Guild
# member argument is an instance of discord.Member
# if no newName is provided, name will update to the one
# stored in the database
async def updateNameRole(server, member, cursor, newName=None):
    if newName == None:
        # grab name from database if none provided
        newName = dbGetName(server, member, cursor)

    # check for existing name role
    for role in member.roles:
        if isNameRole(role, server, cursor):
            await role.edit(name=f"{newName}")
            return

    # if no existing name role, create one
    role = await server.create_role(name=f"{newName}")
    await member.add_roles(role)
    return


# isNameRole checks if a role is a "name role",
# i.e. its name matches a name in the user_list table
def isNameRole(role, server, cursor):
    nameList = dbGetNameList(server, cursor)
    return role.name in nameList


## necessary to link the cog to the main file
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
    return

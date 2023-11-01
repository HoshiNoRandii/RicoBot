### Names ###
# a cog containing RicoBot's naming-related commands

# so that we can use the Discord API
import discord
from discord.ext import commands

from other_cmds import syntaxError, isUserMent

# so that we can use the connection pool to connect
# to the postgres server
from connect import db_connector_with_args


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

    ## setname: set your name
    # syntax: r! setname [name]
    @commands.command(
        name="setname",
        aliases=["setName", "Setname", "SetName"],
        brief="set your name",
        help="""Type `r! setname [name]` to change your name to [name]. This will be the name people see when they use the `getname` command, and will also be listed as a role.\n
Character Limit: 32""",
    )
    @db_connector_with_args
    async def setName(self, ctx, *args, cursor):
        newName = " ".join(args)
        # check that name isn't too long
        if len(newName) > 32:
            await ctx.channel.send("that name is too long! (max: 32 characters)")
            return
        oldName = updateNameDB(ctx.guild, ctx.author, newName, cursor)[0]
        await updateNameRole(ctx.guild, ctx.author, cursor, oldName)
        await ctx.channel.send("name set!")
        return

    ## TODO:
    ## make sure to update the db if somebody
    ## makes manual changes to their name
    # @commands.Cog.listener("on_member_update")
    # async def manualUpdate(self, before, after):


## helper functions ##


# updates a user's name in the user_list table
# server argument is an instance of discord.Guild
# member argument is an instance of discord.Member
# returns (oldName, newName)
def updateNameDB(server, member, newName, cursor):
    serverID = server.id
    userID = member.id
    tableName = f"user_list_{serverID}"

    # get old name
    getOldName = f"""
    SELECT name
    FROM {tableName}
    WHERE user_id = {userID}
    """
    cursor.execute(getOldName)
    oldName = cursor.fetchall()[0][0]

    # set new name
    updateName = f"""
    UPDATE {tableName}
    SET name = '{newName}'
    WHERE user_id = {userID}
    """
    cursor.execute(updateName)
    print(f"user {member.name}'s name set to {newName} in user_list table")

    return (oldName, newName)


# updates a user's name role
# server argument is an instance of discord.Guild
# member argument is an instance of discord.Member
# oldName argument is optional
async def updateNameRole(server, member, cursor, oldName=None):
    # grab name from database
    serverID = server.id
    tableName = f"user_list_{serverID}"
    userID = member.id
    getName = f"""
    SELECT name
    FROM {tableName}
    WHERE user_id = {userID}
    """
    cursor.execute(getName)
    # cursor.fetchall() returns a list of tuples, where each tuple
    # is a returned row
    # this cursor.fetchall() should return [(name,)]
    newName = cursor.fetchall()[0][0]

    # check for existing name role
    for role in member.roles:
        if isNameRole(server, role, cursor, oldName):
            await role.edit(name=f"{newName}")
            return

    # if no existing name role, create one
    role = await server.create_role(name=f"{newName}")
    await member.add_roles(role)
    return


# isNameRole checks if a role is a "name role",
# i.e. its name matches a name in the user_list table
# or the user's previous name, if the optional
# oldName argument is provided
def isNameRole(server, role, cursor, oldName=None):
    # grab list of names from db
    serverID = server.id
    tableName = f"user_list_{serverID}"
    getNames = f"""
    SELECT name
    FROM {tableName}
    """
    cursor.execute(getNames)
    # cursor.fetchall() returns a list of tuples, where each tuple
    # is a returned row
    # this cursor.fetchall() should return
    # [(name1,),(name2,),(name3,),...]
    nameList = listUntuple(cursor.fetchall())
    if oldName:
        nameList.append(oldName)
    print(f"isNameRole {role.name}: {role.name in nameList}")
    print(f"nameList: {nameList}")
    return role.name in nameList


# listUntuple takes a list of tuples and "unpacks" all the tuples,
# returning a list
# ex: listUntuple([(1,), (2,3), (4,)]) == [1, 2, 3, 4]
def listUntuple(tupList):
    retList = []
    for tup in tupList:
        for x in tup:
            retList.append(x)
    return retList


# necessary to link the cog to the main file
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
    return

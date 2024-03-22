### Names ###
# a cog containing RicoBot's naming-related commands

# so that we can use the Discord API
from discord.ext import commands
from database.role_membership import rmUpdate, rmGetUserIDs

from utils import isUserMent, syntaxError

# so that we can use the connection pool to connect
# to the postgres server
from connect import db_connector_no_args, db_connector_with_args

from database.user_list import (
    ulGetName,
    ulUpdateName,
    ulUpdateNickname,
)

from database.bot_roles import brDelete, brUpdate, isNameRole


class CommandsCog(commands.Cog, name="Names"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="nick",
        aliases=["nickname", "Nick", "Nickname", "NickName", "nickName", "NICKNAME"],
        brief="set friends' nicknames",
        help="""Type `r! nick @user1 @user2 @user3 [nickname]` to change the nicknames of every mentioned user to [nickname]. You can include as many people as you want in the same command. If no [nickname] is provided, RicoBot will remove the mentioned users' nicknames.\n
Character Limit: 32\n
Notes:
- Will not work if the first word in the nickname starts with `<@` and ends with `>`.
- RicoBot cannot change the nickname of the server owner. He instead will mention them again and ask them to change their name.""",
    )
    @db_connector_with_args
    async def nick(self, ctx, *args, cursor=None):
        """
        Command to change the nickname of the mentioned people

        syntax: r! nick @user1 @user2 ... [nickname]
        """
        try:
            # check that there are at least 2 arguments
            # and that the first argument is a user mention
            if (len(args) < 1) or (not isUserMent(args[0])):
                await syntaxError(ctx)
                return

            # grab the nickname
            # find where in the message the nickname starts
            # uses the fact that user mentions start with '<@' and end with '>'
            # so the first word in the nickname can't follow this pattern.
            nnameIndex = 0
            while nnameIndex < len(args) and isUserMent(args[nnameIndex]):
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
                await updateNickname(ctx, friend, nname)

        except Exception as error:
            print(error)

        return

    @commands.command(
        name="setname",
        aliases=["setName", "Setname", "SetName", "SETNAME"],
        brief="set your name",
        help="""Type `r! setname [name]` to change your name to [name]. This will be the name people see when they use the `getname` command, and will also be listed as a role.\n
Character Limit: 32""",
    )
    @db_connector_with_args
    async def setName(self, ctx, *args, cursor=None):
        """
        Command to set your own name

        syntax: r! setname [name]
        """
        try:
            newName = " ".join(args)
            # check that name isn't too long
            if len(newName) > 32:
                await ctx.channel.send("that name is too long! (max: 32 characters)")
                return
            await updateName(ctx.guild, ctx.author, cursor, newName)
            await ctx.channel.send("name set!")

        except Exception as error:
            print(error)

        return

    @commands.command(
        name="getname",
        aliases=["getName", "Getname", "GetName", "GETNAME"],
        brief="view friends' names",
        help="""Type `r! getname @user1 @user2 @user3` and I'll tell you the names of the users you mentioned. You can mention as many people as you like.""",
    )
    @db_connector_no_args
    async def getName(self, ctx, *, cursor=None):
        """
        Command to get the name of mentioned server members

        syntax: r! getname @user1 @user2 ...
        """
        try:
            msg = ""
            for friend in ctx.message.mentions:
                # insert newline character if this is not the first friend
                if msg != "":
                    msg = msg + "\n"

                # get name from database
                name = ulGetName(ctx.guild, friend, cursor)

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

    @commands.Cog.listener("on_member_update")
    @db_connector_no_args
    async def memberUpdateListener(self, before, after, *, cursor=None):
        """
        Listener that updates the user_list if somebody changes their nickname

        args:
            before: discord.Member
            after: discord.Member
            cursor: psycopg2.cursor

        returns: None
        """
        try:
            # if nickname changed
            if before.nick != after.nick:
                print("nickname update:")
                ulUpdateNickname(after.guild, after, cursor)

        except Exception as error:
            print(error)

        return

    @commands.Cog.listener("on_guild_role_update")
    @db_connector_no_args
    async def roleUpdateListener(self, before, after, *, cursor=None):
        """
        Listener that updates the bot_roles table if a user edits their name role

        args:
            before: discord.Role
            after: discord.Role
            cursor: psycopg2.cursor

        returns: None
        """
        try:
            # name role update
            if isNameRole(before, cursor):
                print("name role update:")
                brUpdate(after, "name", cursor)
                server = before.guild
                for member in after.members:
                    ulUpdateName(server, member, cursor, after.name)

        except Exception as error:
            print(error)

        return

    @commands.Cog.listener("on_guild_role_delete")
    @db_connector_no_args
    async def roleDeleteListener(self, role, *, cursor=None):
        """
        Listener that will remake a bot-managed role if it is deleted

        args:
            role: discord.Role
            cursor: psycopg2.cursor

        returns: None
        """
        try:
            # name role deleted
            if isNameRole(role, cursor):
                print("name role deleted:")
                # create a new role with the same name
                server = role.guild
                newRole = await server.create_role(name=f"{role.name}")
                # register newRole as managed by RicoBot
                brUpdate(newRole, "name", cursor)
                # assign newRole to all members of (old) role
                for userID in rmGetUserIDs(role, cursor):
                    member = server.get_member(userID)
                    await member.add_roles(newRole)
                    rmUpdate(member, newRole, cursor)
                # remove role from bot_roles table
                brDelete(role, cursor)

        except Exception as error:
            print(error)

        return

    # TODO listen for if somebody is removed from their name role to put them back



## helper functions ##


async def updateNickname(ctx, member, newNick):
    """
    Updates a user's nickname in the server

    memberUpdateListener will push the change through to the user_list table

    args:
        ctx: discord.ext.commands.Context
        member: discord.Member
        newNick: def __str__(self):

    returns: None
    """
    if member == ctx.guild.owner:
        await ctx.channel.send(f"{member.mention} change your nickname!!")
    else:
        await member.edit(nick=newNick)
        # announce that it's been changed
        await ctx.channel.send("nickname changed!")
    return


async def updateName(server, member, cursor, newName=None):
    """
    Updates a user's name role and their name in the user_list and updates the role_membership table

    If no newName is provided, the name role will update to the name stored in the user_list.

    args:
        server: discord.Guild
        member: discord.User
        cursor: psycopg2.cursor
        newName: (optional) str

    returns: None
    """
    if newName == None:
        # grab name from database if none provided
        newName = ulGetName(server, member, cursor)

    # check for existing name role
    for role in member.roles:
        if isNameRole(role, cursor):
            await role.edit(name=f"{newName}")
            # listener will push newName to db
            return

    # if no existing name role, create one
    role = await server.create_role(name=f"{newName}")
    await member.add_roles(role)
    brUpdate(role, "name", cursor)  # register role as managed by RicoBot
    rmUpdate(member, role, cursor)  # register user and role to role_membership table
    ulUpdateName(server, member, cursor, newName)
    return


## necessary to link the cog to the main file
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
    return

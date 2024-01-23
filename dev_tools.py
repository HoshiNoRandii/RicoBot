### Dev Tools ###
# a cog containing commands for developer use

# so that we can use the Discord API
import discord
from discord.ext import commands

from functools import wraps
import inspect
import asyncio

# so that we can use the connection pool to connect
# to the postgres server
# creates an async function
from connect import db_connector_no_args, db_connector_with_args

from database import (
    dbGetDevFlag,
)

from names import updateName


# decorator function to add to dev-only commands
# decorator should come after db_connector decorator
# any function wrapped with dev_only must have
# (self, ctx) as the first two arguments and
# cursor as a keyword only argument
# and also must be an async function
def dev_only(func):
    # wrapper function
    @wraps(func)
    async def inner(self, ctx, *args, cursor=None, **kwargs):
        print("Checking dev status...")
        if "cursor" in inspect.getfullargspec(func).kwonlyargs:
            # if user is a dev
            if dbGetDevFlag(ctx.guild, ctx.author, cursor):
                print("dev status confirmed")
                kwargs["cursor"] = cursor
                await func(self, ctx, *args, **kwargs)
                return
            # if user is not a dev
            else:
                print("not a dev")
                await ctx.channel.send("you aren't allowed to do that \:/")
                return
        return

    return inner


class CommandsCog(commands.Cog, name="Dev Tools"):
    def __init__(self, bot):
        self.bot = bot

    ## createUserList: create and update the user_list table in the database
    # user_list table has the columns:
    #   user_id, username, name, pronouns, nickname, dev_flag
    @commands.command(
        name="createUserList",
        brief="create user_list table",
        help="create user_list table",
    )
    @db_connector_no_args
    async def createUserList(self, ctx, *, cursor=None):
        try:
            # create table
            serverID = ctx.guild.id
            tableName = f"user_list_{serverID}"
            createTable = f"""
            CREATE TABLE IF NOT EXISTS {tableName} (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                name TEXT,
                pronouns TEXT,
                nickname TEXT,
                dev_flag BOOL
            )
            """
            cursor.execute(createTable)
            print("user_list table exists")

            # populate table
            for member in ctx.guild.members:
                mUserID = member.id
                mUsername = member.name
                mNickname = member.nick
                insertInto = f"""
                INSERT INTO {tableName} (user_id, username, nickname, dev_flag)
                VALUES ({mUserID}, '{mUsername}', '{mNickname}', FALSE)
                ON CONFLICT (user_id)
                DO
                    UPDATE SET username = '{mUsername}',
                               nickname = '{mNickname}'
                """
                cursor.execute(insertInto)
            print("user_list table populated")

        except Exception as error:
            print(error)

        return

    ## forbidden: check if you are a dev in the db
    @commands.command(
        name="forbidden",
        brief="test dev status",
        help="test dev status",
    )
    @db_connector_no_args
    @dev_only
    async def forbidden(self, ctx, *, cursor=None):
        await ctx.channel.send("\:)")
        return

    ## checkUserOrder: check the order that users are
    # listed in ctx.guild.members
    @commands.command(
        name="checkUserOrder",
        brief="check the order that users are listed in ctx.guild.members",
        help="check the order that users are listed in ctx.guild.members",
    )
    @db_connector_no_args
    @dev_only
    async def checkUserOrder(self, ctx, *, cursor=None):
        msg = ""
        for member in ctx.guild.members:
            msg = msg + f"{member.name} "
        await ctx.channel.send(msg)

    ## devInsertNames: update the entire name column
    # in the user_list table
    @commands.command(
        name="devInsertNames",
        brief="update the entire name column in the user_list table",
        help="update the entire name column in the user_list table; be sure to use checkUserOrder first",
    )
    @db_connector_with_args
    @dev_only
    async def devInsertNames(self, ctx, *args, cursor=None):
        # grab list of usernames
        unameList = list(map(lambda x: x.name, ctx.guild.members))

        # zip with list of names to add to db
        updateListReadable = list(zip(unameList, args))

        await ctx.channel.send(f"Does this look right? \n{updateListReadable}")

        def check(msg):
            return msg.channel == ctx.channel

        try:
            # wait for approval
            ans = await self.bot.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.channel.send("You took too long to approve the list! Start over.")
        else:
            # if it does not look right
            if ans.content not in ["y", "Y", "yes", "Yes", "YES"]:
                await ctx.channel.send(f"Oops. Start the command over.")
                return

            # if it does look right
            # updateList with (Discord.member, str) entries
            updateList = list(zip(ctx.guild.members, args))
            for tup in updateList:
                await updateName(ctx.guild, tup[0], cursor, tup[1])
            await ctx.channel.send("Names updated!")

        return


# necessary to link the cog to the main file
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
    return

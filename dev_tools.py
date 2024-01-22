### Dev Tools ###
# a cog containing commands for developer use

# so that we can use the Discord API
import discord
from discord.ext import commands

from functools import wraps
import inspect

# so that we can use the connection pool to connect
# to the postgres server
# creates an async function
from connect import (
    db_connector_no_args,
    db_connector_with_args,
    dbGetDevFlag,
    dbUpdateNameCol,
)


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

    ## devInsertNames: update the entire name column
    # in the user_list table
    @commands.command(
        name="devInsertNames",
        brief="update the entire name column in the user_list table",
        help="update the entire name column in the user_list table; be sure to check the current order of users in the table",
    )
    @db_connector_with_args
    @dev_only
    async def devInsertNames(self, ctx, *args, cursor=None):
        dbUpdateNameCol(args, ctx.guild, cursor)
        return


# necessary to link the cog to the main file
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
    return

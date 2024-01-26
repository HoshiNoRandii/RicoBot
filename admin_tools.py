### Admin Tools ###
# a cog containing commands for admin use

# so that we can use the Discord API
from discord.ext import commands

from functools import wraps
import inspect
import asyncio

# so that we can use the connection pool to connect
# to the postgres server
# creates an async function
from connect import db_connector_no_args, db_connector_with_args
from database.bot_roles import brCreate

from database.user_list import (
    ulCreate,
    ulGetAdminFlag,
    ulPopulate,
)

from names import updateName


# decorator function to add to admin-only commands
# decorator should come after db_connector decorator
# any function wrapped with admin_only must have
# (self, ctx) as the first two arguments and
# cursor as a keyword only argument
# and also must be an async function
def admin_only(func):
    # wrapper function
    @wraps(func)
    async def inner(self, ctx, *args, cursor=None, **kwargs):
        print("Checking admin status...")
        if "cursor" in inspect.getfullargspec(func).kwonlyargs:
            # if user is a admin
            if ulGetAdminFlag(ctx.guild, ctx.author, cursor):
                print("admin status confirmed")
                kwargs["cursor"] = cursor
                await func(self, ctx, *args, **kwargs)
                return
            # if user is not a admin
            else:
                print("not a admin")
                await ctx.channel.send("you aren't allowed to do that \:/")
                return
        return

    return inner


class CommandsCog(commands.Cog, name="Admin Tools"):
    def __init__(self, bot):
        self.bot = bot

    ## createUserList: create and update the user_list table in the database
    # user_list table has the columns:
    #   user_id, username, name, pronouns, nickname, admin_flag
    @commands.command(
        name="createUserList",
        brief="create user_list table",
        help="create user_list table",
    )
    @db_connector_no_args
    @admin_only
    async def createUserList(self, ctx, *, cursor=None):
        ulCreate(ctx.guild, cursor)
        ulPopulate(ctx.guild, cursor)
        return

    ## createBotRoleList: create the bot_roles table in the database
    # bot_roles table has the columns:
    #   role_id, type, name, member
    @commands.command(
        name="createBotRoleList",
        brief="create bot_roles table",
        help="create bot_roles table",
    )
    @db_connector_no_args
    @admin_only
    async def createBotRoleList(self, ctx, *, cursor=None):
        brCreate(ctx.guild, cursor)
        return

    ## forbidden: check if you are a admin in the db
    @commands.command(
        name="forbidden",
        brief="test admin status",
        help="test admin status",
    )
    @db_connector_no_args
    @admin_only
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
    @admin_only
    async def checkUserOrder(self, ctx, *, cursor=None):
        msg = ""
        for member in ctx.guild.members:
            msg = msg + f"{member.name} "
        await ctx.channel.send(msg)

    ## adminInsertNames: update the entire name column
    # in the user_list table
    @commands.command(
        name="adminInsertNames",
        brief="update the entire name column in the user_list table",
        help="update the entire name column in the user_list table; be sure to use checkUserOrder first",
    )
    @db_connector_with_args
    @admin_only
    async def adminInsertNames(self, ctx, *args, cursor=None):
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
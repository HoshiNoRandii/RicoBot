### Dev Tools ###
# a cog containing commands for developer use

# so that we can use the Discord API
import discord
from discord.ext import commands

# so that we can use the connection pool to connect
# to the postgres server
# creates an async function
from connect import db_connector_no_args


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


# necessary to link the cog to the main file
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
    return

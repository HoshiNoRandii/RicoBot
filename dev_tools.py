### Dev Tools ###
# a cog containing commands for developer use

# so that we can use the Discord API
import discord
from discord.ext import commands

# so that we can use the connection pool to connect
# to the postgres server
from connect import db_connector


class CommandsCog(commands.Cog, name="Dev Tools"):
    def __init__(self, bot):
        self.bot = bot

    ## createUserList: create and update the user_list table in the database
    # user_list table has the columns:
    #   user_id, username, name, pronouns, nickname
    @commands.command(
        name="createUserList",
        brief="create user_list table",
        help="create user_list table",
    )
    @db_connector
    def createUserList(self, ctx, cursor):
        # create table
        serverID = ctx.guild.id
        tableName = f"user_list_{serverID}"
        createTable = f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            name TEXT,
            pronouns TEXT,
            nickname TEXT
        )
        """
        cursor.execute(createTable)
        print("user_list table exists")

        # populate table
        for member in ctx.guild.members:
            mUser_id = str(member.id)
            mUsername = member.name
            mNickname = member.nick
            command = f"""
            INSERT INTO {tableName} (user_id, username, nickname)
            VALUES ({mUser_id}, '{mUsername}', '{mNickname}')
            ON CONFLICT (user_id)
            DO
                UPDATE SET username = '{mUsername}',
                           nickname = '{mNickname}'
            """
            cursor.execute(command)
        print("user_list table populated")

        return


# necessary to link the cog to the main file
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
    return

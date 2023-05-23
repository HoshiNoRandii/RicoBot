### Dev Commands ###
# a cog containing commands for developer use

# so that we can use the Discord API
import discord
from discord.ext import commands

class CommandsCog(commands.Cog, name = 'Dev Commands'):

    def __init__(self, bot):
        self.bot = bot

    ## userList: create or update the id_info table in the database
    # id_info table has the columns: user_id, name, nickname
    @commands.command(name = 'userList', brief = 'update id_info',\
            help = 'update id_info')
    async def userList(self,ctx):
        return




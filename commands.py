### Commands ###
# a cog containing all of RicoBot's commands

# so that we can use the Discord API
import discord
from discord.ext import commands


class CommandsCog(commands.Cog, name = 'Commands'):

    def __init__(self, bot):
        self.bot = bot

    # nick: change the nickname of the mentioned people
    # syntax: r! nick @user1 @user2 ... [nickname]
    # NOTE: only works on correct syntax
    # still need to implement error messages for incorrect syntax
    @commands.command(name = 'nick',\
            brief = 'set friends\' nicknames',\
            help = 'Type `r! nick @user1 @user2 @user3 [nickname]`\
            to change the nicknames of every mentioned user to [nickname].\
            You can include as many people as you want in the same command.\n\
            \nNotes:\n\
            \t- will not work if the first word in the nickname is\
            enclosed in <angle brackets>.\n\
            \t- RicoBot cannot change the nickname of the server owner. He\
            instead will mention them again and ask them to change their name.')
    async def nick(self, ctx, *args):
        # grab the nickname
        # find where in the message the nickname starts
        # uses the fact that mentions start with '<' and end with '>'
        # so the first word in the nickname can't be in angle brackets
        nnameIndex = 0
        while args[nnameIndex].startswith('<')\
                and args[nnameIndex].endswith('>'):  
            nnameIndex +=1
        # slice off the nickname
        nnameList = args[nnameIndex:]
        # make it one string again
        nname = ' '.join(nnameList)

        # give the nickname to every mentioned user
        for friend in ctx.message.mentions:
            if friend == ctx.guild.owner:
                await ctx.channel.send(\
                        f'{friend.mention} change your nickname!!')
            else:
                await friend.edit(nick = nname)
        # announce that it's been changed
        await ctx.channe.send('nickname changed!')
        return


    # hi: send 'henlo!'
    @commands.command(name = 'hi', brief = 'say hi!',\
            help = 'Type `r! hi` to say hi to RicoBot.')
    async def hi(self,ctx):
        await ctx.channel.send('henlo!')
        return


    # help: a custom help command
    @commands.command(name = 'help',\
            brief = 'show this help dialogue',\
            help = 'Really now? Clearly you got this.')
    async def help(self, ctx, *args):
        # general help
        if len(args) == 0:
            # start building embed
            emb = discord.Embed(\
                    title = 'RicoBot Help',\
                    description = 'Here\'s a list of all of RicoBot\'s\
                    commands. For more information on a specific command,\
                    type `r! help [command name]`.',\
                    color = discord.Color.dark_gold())
            # iterate through each cog
            for cog in self.bot.cogs:
                cmdList = []
                # self.bot.cogs is a dictionary whose entries have the name of
                # the cog as a key and the cog itself as the value.
                # when we iterate, we just get the keys. need to use them
                # like indexes to grab the value.
                for cmd in self.bot.cogs[cog].walk_commands():
                    # only add commands that aren't hidden
                    if not cmd.hidden:
                        cmdList.append(f'{cmd.name}: *{cmd.brief}*')
                if len(cmdList) > 0:
                    cmdList.sort()
                    cmdList = '\n'.join(cmdList)
                    # add to embed
                    emb.add_field(name = cog,\
                            value = cmdList,\
                            inline = False)

        # specific command help
        elif len(args) == 1:
            # get the command
            cmd = self.bot.get_command(args[0])
            # build the embed
            emb = discord.Embed(\
                    title = 'RicoBot Help',\
                    color = discord.Color.dark_gold())
            emb.add_field(name = cmd.name,\
                    value = cmd.help,\
                    inline = False)

        # send the embed
        await ctx.channel.send(embed = emb)


# necessary to link the cog to the main file
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))

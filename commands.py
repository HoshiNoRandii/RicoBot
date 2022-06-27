### Commands ###
# a cog containing all of RicoBot's commands

# so that we can use the Discord API
import discord
from discord.ext import commands


## function to handle syntax erros
# will be called from various commands or events
async def syntaxError(ctx):
    syntaxErrorMsg = 'Um... I\'m not exactly sure what you\'re asking for.\
 Make sure you don\'t have any extra spaces in your message.\
 You can type `r! help` for a list of valid commands, or `r! help [command]`\
 for information about a specific command.'
    await ctx.channel.send(syntaxErrorMsg)
    return


class CommandsCog(commands.Cog, name = 'Commands'):

    def __init__(self, bot):
        self.bot = bot

    ## nick: change the nickname of the mentioned people
    # syntax: r! nick @user1 @user2 ... [nickname]
    @commands.command(name = 'nick',\
            brief = 'set friends\' nicknames',\
            help = 'Type `r! nick @user1 @user2 @user3 [nickname]`\
            to change the nicknames of every mentioned user to [nickname].\
            You can include as many people as you want in the same command.\n\
            \nCharacter Limit: 32\n\
            \nNotes:\n\
            \t- Will not work if the first word in the nickname starts with\
            \'<@\' and ends with \'>\'.\
            \t- RicoBot cannot change the nickname of the server owner. He\
            instead will mention them again and ask them to change their name.')
    async def nick(self, ctx, *args):
        # check that the first arguments is a user mention 
        if not (args[0].startswith('<@') and args[0].endswith('>')):
                await syntaxError(ctx) 
                return

        # grab the nickname
        # find where in the message the nickname starts
        # uses the fact that user mentions start with '<@' and end with '>'
        # so the first word in the nickname can't follow this pattern.
        nnameIndex = 0
        while args[nnameIndex].startswith('<@')\
                and args[nnameIndex].endswith('>'):  
            nnameIndex +=1
        # slice off the nickname
        nnameList = args[nnameIndex:]
        # make it one string again
        nname = ' '.join(nnameList)
        # check that it isn't too long
        if len(nname) > 32:
            await ctx.channel.send(\
                    'that nickname is too long! (max: 32 characters)')
            return

        # give the nickname to every mentioned user
        for friend in ctx.message.mentions:
            if friend == ctx.guild.owner:
                await ctx.channel.send(\
                        f'{friend.mention} change your nickname!!')
            else:
                await friend.edit(nick = nname)
        # announce that it's been changed
        await ctx.channel.send('nickname changed!')
        return


    ## hi: send 'henlo!'
    @commands.command(name = 'hi', brief = 'say hi!',\
            help = 'Type `r! hi` to say hi to RicoBot.')
    async def hi(self,ctx):
        await ctx.channel.send('henlo!')
        return

# servername commented out because it doesn't seem that discord.py
# allows for changing the server name for now
'''
    ## servername: set the server name
    # syntax: r! servername [name]
    @commands.command(name = 'servername',\
            brief = 'set the server name',\
            help = 'Type `r! servername [name]` to change the name of the\
            server to [name].\n\
            \nCharacter Limit: 100')
    async def servername(self, ctx, *args):
        if len(args) > 100:
            ctx.channel.send('that name is too long! (max: 100 characters)')
            return
        await ctx.guild.set_name(args)
        await ctx.channel.send('server name changed!')
        return
'''      

    ## help: a custom help command
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
        return


    ## detect when somebody has tried to call RicoBot but has used an
    # invalid command
    @commands.Cog.listener('on_message')
    # only care if it seems like they were trying to call Rico
    async def invalidCmd(self, message):
        # only care if it seems like they were trying to call Rico
        if message.content.startswith('r!')\
                or message.content.startswith('R!'):
            # remove the prefix
            # ultimately trying to isolate the "command" to check that
            # it is not on the valid list
            cmd = message.content[2:]
            # remove the space after the prefix too if it's there
            # but only one. one is allowed per his usual prefix.
            # too many spaces will mean syntax error
            if cmd.startswith(' '):
                cmd = cmd[1:]
            # grab just the next word after the prefix,
            # including leading whitespace
            endInd = 0
            # first get past all starting whitespace
            while endInd < len(cmd)-1 and cmd[endInd].isspace():
                endInd += 1
            # now go until the next whitespace
            while endInd < len(cmd)-1 and not cmd[endInd].isspace():
                endInd += 1
            # set cmd to be that first word, including leading whitespace
            cmd = cmd[:endInd]
            # check that it is not a valid command or command alias
            for validCmd in self.bot.commands:
                if cmd == validCmd.name:
                    return
                if cmd in validCmd.aliases:
                    return
            # send error messgage
            await syntaxError(message)
        return


# necessary to link the cog to the main file
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
    return

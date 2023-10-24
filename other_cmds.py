### Other Commands ###
# a cog containing RicoBot's uncategorized commands

# so that we can use the Discord API
import discord
from discord.ext import commands


## function to handle syntax erros
# will be called from various commands or events
async def syntaxError(ctx):
    syntaxErrorMsg = "Um... I'm not exactly sure what you're asking for.\
 Make sure you don't have any extra spaces in your message.\
 You can type `r! help` for a list of valid commands, or `r! help [command]`\
 for information about a specific command."
    await ctx.channel.send(syntaxErrorMsg)
    return


## isUserMent(word): str -> bool
# returns True if word is a user mention
# uses the fact that user mentions begin with <@ and end with >
# assumes that word does not contain any whitespace
def isUserMent(word):
    return word.startswith("<@") and word.endswith(">")


class CommandsCog(commands.Cog, name="Other Commands"):
    def __init__(self, bot):
        self.bot = bot

    ## hi: send 'henlo!'
    @commands.command(
        name="hi", brief="say hi!", help="Type `r! hi` to say hi to RicoBot."
    )
    async def hi(self, ctx):
        await ctx.channel.send("henlo!")
        return

    ## servername: set the server name
    # syntax: r! servername [name]
    @commands.command(
        name="servername",
        brief="set the server name",
        help="Type `r! servername [name]` to change the name of the\
            server to [name].\n\
            \nCharacter Limit: 100",
    )
    async def servername(self, ctx, *args):
        if len(" ".join(args)) > 100:
            ctx.channel.send("that name is too long! (max: 100 characters)")
            return
        await ctx.guild.edit(name=" ".join(args))
        await ctx.channel.send("server name changed!")
        return

    ## help: a custom help command
    @commands.command(
        name="help",
        brief="show this help dialogue",
        help="Really now? Clearly you got this.",
    )
    async def help(self, ctx, *args):
        emb = None

        # general help
        if len(args) == 0:
            # start building embed
            emb = discord.Embed(
                title="RicoBot Help",
                description="Here's a list of all of RicoBot's\
                    commands. For more information on a specific command,\
                    type `r! help [command name]`.",
                color=discord.Color.dark_gold(),
            )
            # generator to not include dev_tools cog
            # in the help command
            cog_generator = (x for x in self.bot.cogs if x != "Dev Tools")
            # iterate thru cogs
            for cog in cog_generator:
                cmdList = []
                # self.bot.cogs is a dictionary whose entries have the name of
                # the cog as a key and the cog itself as the value.
                # when we iterate, we just get the keys. need to use them
                # like indexes to grab the value.
                for cmd in self.bot.cogs[cog].walk_commands():
                    # only add commands that aren't hidden
                    if not cmd.hidden:
                        cmdList.append(f"{cmd.name}: *{cmd.brief}*")
                if len(cmdList) > 0:
                    cmdList.sort()
                    cmdList = "\n".join(cmdList)
                    # add to embed
                    emb.add_field(name=cog, value=cmdList, inline=False)

        # specific command help
        elif len(args) == 1:
            # get the command
            cmd = self.bot.get_command(args[0])
            # check if it's a valid command
            if cmd == None:
                await ctx.channel.send(
                    "That's not something I can do. \
Type `r! help` for a list of valid commands."
                )
            # build the embed
            emb = discord.Embed(title="RicoBot Help", color=discord.Color.dark_gold())
            emb.add_field(name=cmd.name, value=cmd.help, inline=False)

        # if too many arguments
        elif len(args) > 1:
            await ctx.channel.send(
                "That's too much! Ask about one \
command at a time please!"
            )
            return

        # send the embed
        if emb:
            await ctx.channel.send(embed=emb)
        return

    ## detect when somebody has tried to call RicoBot but has used an
    # invalid command
    @commands.Cog.listener("on_message")
    # only care if it seems like they were trying to call Rico
    async def invalidCmd(self, message):
        # only care if it seems like they were trying to call Rico
        if message.content.startswith("r!") or message.content.startswith("R!"):
            # remove the prefix
            # ultimately trying to isolate the "command" to check that
            # it is not on the valid list
            cmd = message.content[2:]
            # remove the space after the prefix too if it's there
            # but only one. one is allowed per his usual prefix.
            # too many spaces will mean syntax error
            if cmd.startswith(" "):
                cmd = cmd[1:]
            # grab just the next word after the prefix,
            # including leading whitespace
            endInd = 0
            # first get past all starting whitespace
            while endInd < len(cmd) and cmd[endInd].isspace():
                endInd += 1
            # now go until the next whitespace
            while endInd < len(cmd) and not cmd[endInd].isspace():
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

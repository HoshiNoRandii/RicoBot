### helpful functions that did not fit into other categories


def isUserMent(word):
    """
    Check if a string is a user mention

    Relies on the fact that user mentions begin with <@ and end with >

    Assumes that word does not contain any whitespace

    args:
        word: str

    returns: Bool
    """
    return word.startswith("<@") and word.endswith(">")


async def syntaxError(ctx):
    """
    Function to call whenever a syntax error is detected

    RicoBot will simply let the user know that he cannot understand their command.

    args:
        ctx: discord.ext.commands.Context

    returns: None
    """
    syntaxErrorMsg = """Um... I'm not exactly sure what you're asking for.
Make sure you don't have any extra spaces in your message.
You can type `r! help` for a list of valid commands, or `r! help [command]` for information about a specific command."""
    await ctx.channel.send(syntaxErrorMsg)
    return

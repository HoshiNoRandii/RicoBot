# RicoBot

RicoBot is a bot for my server with my friends.
He requires full admin permissions to function fully, so he should not be used
in large servers with lots of strangers.

## Commands

### hi

Type `r! hi` to say hi to RicoBot (and test that he is online).

### nick

Type `r! nick @user1 @user2 ... [nickname]` to change the nicknames of every
mentioned user to [nickname]. You can include as many people as you want in
the same command.

Character Limit: 32

**Notes:**
- Will not work if the first word in the nickname starts with `<@` and ends with `>`
- RicoBot cannot change the nickname of the server owner. He instead will mention them again and ask them to change their name.

### servername

Type `r! servername [name]` to change the name of the server to [name].

Character Limit: 100

### help

Type `r! help` for a list of RicoBot's commands.
For information on a specific command, type `r! help [command name]`.

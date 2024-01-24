### functions related to the bot_roles table in the database
### bot_roles table stores information about all roles managed
### by RicoBot

# columns in the bot_roles table
botRolesColumns = ["role_id", "type", "name"]
botRolesTypes = ["name"]

### TODO get this and the user_list table created on init
### still need to test all these funcs!


# create the bot_roles table
# server: discord.Guild
def brCreate(server, cursor):
    try:
        serverID = server.id
        tableName = f"bot_roles_{serverID}"
        createTable = f"""
            CREATE TABLE IF NOT EXISTS {tableName} (
                role_id BIGINT PRIMARY KEY,
                type TEXT,
                name TEXT
            )
            """
        cursor.execute(createTable)
        print("bot_roles table exists")

    except Exception as error:
        print(error)

    return




# update role info in bot_roles table
# if role is not already in the table, insert it
# role: discord.Role
def brUpdate(role, brType, cursor):
    # check that type is valid
    if brType not in botRolesTypes:
        print(f'invalid bot role type "{brType}"')
        return
    # type valid, insert or update
    try:
        serverID = role.guild.id
        tableName = f"bot_roles_{serverID}"
        roleID = role.id
        roleName = role.name
        insertInto = f"""
            INSERT INTO {tableName} (role_id, type, name)
            VALUES ({roleID}, '{brType}', '{roleName}')
            ON CONFLICT (role_id)
            DO
                UPDATE SET name = '{roleName}'
            """
        cursor.execute(insertInto)
        print(f"{roleName} role updated in bot_roles table")

    except Exception as error:
        print(error)

    return


# check if a role is a role managed by RicoBot
# role: discord.Role
def isBotRole(role, cursor):
    return brGetType(role, cursor) != None


# get the type of a role
# role: discord.Role
def brGetType(role, cursor):
    try:
        serverID = role.guild.id
        tableName = f"bot_roles_{serverID}"
        roleID = role.id
        select = f"""
           SELECT type FROM {tableName}
           WHERE role_id = {roleID}
           """
        cursor.execute(select)
        # cursor.fetchall() returns a list of tuples, where each tuple
        # is a returned row
        # if the role is in the table,
        # this cursor.fetchall() should return [(type,)]
        # otherwise it should return []
        matches = cursor.fetchall()

        if matches == []:
            print(f"{role.name} role is not managed by RicoBot")
            return

        else:
            return matches[0][0]

    except Exception as error:
        print(error)

    return


# check if a role is of a specified type
# role: discord.Role
def isTypeRole(role, brType, cursor):
    # check that type is valid
    if brType not in botRolesTypes:
        print(f'invalid bot role type "{brType}"')
        return
    # type is valid, check role
    return brGetType(role, cursor) == brType


# check if a role is a name role
# role: discord.Role
def isNameRole(role, cursor):
    return isTypeRole(role, "name", cursor)

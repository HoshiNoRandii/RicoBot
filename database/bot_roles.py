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
        print("Creating bot_roles table...")
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


## update functions ##


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


# remove a role from the bot_roles table
def brDelete(role, cursor):
    try:
        serverID = role.guild.id
        tableName = f"bot_roles_{serverID}"
        roleID = role.id
        delete = f"""
        DELETE FROM {tableName}
        WHERE role_id = {roleID}
        """
        cursor.execute(delete)
        print(f"{role.name} role removed from bot_roles table")

    except Exception as error:
        print(error)

    return


## get functions ##


# get info about a role
# role: discord.Role
def brGet(column, role, cursor):
    # check that column is valid
    if column not in botRolesColumns:
        print(f'no column named "{column}" in bot_role table')
        return
    # column is valid, grab info
    try:
        serverID = role.guild.id
        tableName = f"bot_roles_{serverID}"
        roleID = role.id
        select = f"""
           SELECT {column} FROM {tableName}
           WHERE role_id = {roleID}
           """
        cursor.execute(select)
        # cursor.fetchall() returns a list of tuples, where each tuple
        # is a returned row
        # if the role is in the table,
        # this cursor.fetchall() should return [(info,)]
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


# get the type of a role
# role: discord.Role
def brGetType(role, cursor):
    return brGet("type", role, cursor)


## Bool functions ##


def isBotRole(role, cursor):
    """
    Check if a role is managed by RicoBot

    args:
        role: discord.Role
        cursor: psycopg2.cursor

    returns: Bool
    """
    return brGetType(role, cursor) != None


def isTypeRole(role, brType, cursor):
    """
    Check if a role is of a specified type

    args:
        role: discord.Role

        brType: str
            brType should be a member of botRolesTypes

        cursor: psycopg2.cursor

    returns: Bool
    """
    # check that type is valid
    if brType not in botRolesTypes:
        print(f'invalid bot role type "{brType}"')
        return
    # type is valid, check role
    return brGetType(role, cursor) == brType


def isNameRole(role, cursor):
    """
    Check if a role is a name role

    args:
        role: discord.Role
        cursor: psycopg2.cursor

    returns: Bool
    """
    return isTypeRole(role, "name", cursor)

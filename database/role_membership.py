### functions related to the role_membership table in the database
### role_membership table stores information about which users
### are assigned to which of the roles managed by RicoBot

# columns in the role_membership table
from database.bot_roles import isBotRole


roleMembershipColumns = ["user_id", "role_id"]


def rmCreate(server, cursor):
    """
    Create the role_membership table

    The role_membership table stores information about which users are assigned to which of the roles managed by RicoBot. Each row contains a user_id and a role_id for a role that the user is assigned to.

    args:
        server: discord.Guild
            the discord server that the table corresponds to
        cursor: psycopg2.cursor

    returns: None
    """
    try:
        print("Creating role_membership table...")
        serverID = server.id
        tableName = f"role_membership_{serverID}"
        createTable = f"""
            CREATE TABLE IF NOT EXISTS {tableName} (
            user_id BIGINT REFERENCES user_list_{serverID}(user_id) ON DELETE CASCADE,
            role_id BIGINT REFERENCES bot_roles_{serverID}(role_id) ON DELETE CASCADE
        )
        """
        cursor.execute(createTable)
        print("role_membership table exists")

    except Exception as error:
        print(error)

    return


def rmUpdate(user, role, cursor):
    """
    Add a row to the role_membership table

    args:
        user: discord.Member
        role: discord.Role
        cursor: psycopg2.cursor

    returns: None
    """
    try:
        # check if role is managed by RicoBot
        if not isBotRole(role, cursor):
            return
        # role is managed by RicoBot, add row to table
        serverID = role.guild.id
        tableName = f"role_membership_{serverID}"
        userID = user.id
        roleID = role.id
        insertInto = f"""
            INSERT INTO {tableName} (user_id, role_id)
            VALUES ({userID}, {roleID})
        """
        cursor.execute(insertInto)
        print(
            f"{user.name} registered as a member of {role.name} role in role_membership table"
        )

    except Exception as error:
        print(error)

    return


def rmGetUserIDs(role, cursor):
    """
    Generator function that yields user ID's of
    members of the given role.

    args:
        role: discord.Role
        cursor: psycopg2.cursor

    yields: int
    """
    try:
        serverID = role.guild.id
        tableName = f"role_membership_{serverID}"
        roleID = role.id
        select = f"""
            SELECT user_id FROM {tableName}
            WHERE role_id = {roleID}
        """
        cursor.execute(select)
        # cursor.fetchall() returns a list of tuples,
        # where each tuple is a returned row
        # this cursor.fetchall returns [(id,)]
        members = cursor.fetchall()

        for (member,) in members:
            yield member

    except Exception as error:
        print(error)

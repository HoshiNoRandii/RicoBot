### functions related to the role_membership table in the database
### role_membership table stores information about which users
### are assigned to which of the roles managed by RicoBot

# columns in the role_membership table
roleMembershipColumns = ["user_id", "role_id"]


# create the role_membership table
# server: discord.Guild
def rmCreate(server, cursor):
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

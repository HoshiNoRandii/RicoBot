### functions related to the user_list table in the database

# columns in the user_list table
userListColumns = ["user_id", "username", "name", "pronouns", "nickname", "admin_flag"]


# create the user_list table
# server: discord.Guild
def ulCreate(server, cursor):
    try:
        # create table
        serverID = server.id
        tableName = f"user_list_{serverID}"
        createTable = f"""
           CREATE TABLE IF NOT EXISTS {tableName} (
               user_id BIGINT PRIMARY KEY,
               username TEXT,
               name TEXT,
               pronouns TEXT,
               nickname TEXT,
               admin_flag BOOL
           )
           """
        cursor.execute(createTable)
        print("user_list table exists")

    except Exception as error:
        print(error)

    return


# populate or update the entire user_list table
# server: discord.Guild
def ulPopulate(server, cursor):
    try:
        serverID = server.id
        tableName = f"user_list_{serverID}"

        for member in server.members:
            mUserID = member.id
            mUsername = member.name
            mNickname = member.nick
            insertInto = f"""
               INSERT INTO {tableName} (user_id, username, nickname, admin_flag)
               VALUES ({mUserID}, '{mUsername}', '{mNickname}', FALSE)
               ON CONFLICT (user_id)
               DO
                   UPDATE SET username = '{mUsername}',
                              nickname = '{mNickname}'
               """
            cursor.execute(insertInto)
        print("user_list table populated")

    except Exception as error:
        print(error)

    return


# set admin_flag of all users in adminList to True
# adminIDList is a list of user ID's
def ulAdminInit(adminIDList, server, cursor):
    try:
        serverID = server.id
        tableName = f"user_list_{serverID}"

        for userID in adminIDList:
            update = f"""
            UPDATE {tableName}
            SET admin_flag = TRUE
            WHERE user_id = {userID}
            """
            cursor.execute(update)
        print("admin admin_flags set to True")

    except Exception as error:
        print(error)

    return


# get functions


# gets a user's info from the selected column
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
def ulGet(column, server, member, cursor):
    # check that column is valid
    if column not in userListColumns:
        print(f'no column named "{column}" in user_list table')
        return
    # column is valid, grab info
    ret = None
    try:
        serverID = server.id
        userID = member.id
        tableName = f"user_list_{serverID}"
        select = f"""
        SELECT {column}
        FROM {tableName}
        WHERE user_id = {userID}
        """
        cursor.execute(select)
        # cursor.fetchall() returns a list of tuples, where each tuple
        # is a returned row
        # this cursor.fetchall() should return [(info,)]
        ret = cursor.fetchall()[0][0]

    except Exception as error:
        print(error)

    return ret


# fetches an entire column from the user_list table
# server arg is an instance of discord.Guild
def ulGetList(column, server, cursor):
    # check that column is valid
    if column not in userListColumns:
        print(f'no column named "{column}" in user_list table')
        return
    # column is valid, grab info
    retList = None
    try:
        serverID = server.id
        tableName = f"user_list_{serverID}"
        select = f"""
        SELECT {column}
        FROM {tableName}
        """
        cursor.execute(select)
        # cursor.fetchall() returns a list of tuples, where each tuple
        # is a returned row
        # this cursor.fetchall() should return
        # [(info1,),(info2,),(info3,),...]
        retList = listUntuple(cursor.fetchall())

    except Exception as error:
        print(error)

    return retList


# listUntuple takes a list of tuples and "unpacks" all the tuples,
# returning a list
# ex: listUntuple([(1,), (2,3), (4,)]) == [1, 2, 3, 4]
def listUntuple(tupList):
    retList = []
    for tup in tupList:
        for x in tup:
            retList.append(x)
    return retList


# gets a user's name from the database
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
def ulGetName(server, member, cursor):
    return ulGet("name", server, member, cursor)


# gets a user's pronouns from the database
# server arg is an instance or discord.Guild
# member arg is an instance of discord.Member
def ulGetPronouns(server, member, cursor):
    return ulGet("pronouns", server, member, cursor)


# gets a user's admin status from the database
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
def ulGetAdminFlag(server, member, cursor):
    return ulGet("admin_flag", server, member, cursor)


# gets the list of all user id's in the database
# server arg is an instance of discord.Guild
def ulGetUIDList(server, cursor):
    return ulGetList("user_id", server, cursor)


# gets the list of all names in the database
# server arg is an instance of discord.Guild
def ulGetNameList(server, cursor):
    return ulGetList("name", server, cursor)


# gets the list of all the pronoun sets
# in the database
# server arg is an instance of discord.Guild
def ulGetPronounList(server, cursor):
    return ulGetList("pronouns", server, cursor)


# update functions


# udpate a user's info in the database in the selected column
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
def ulUpdate(column, newInfo, server, member, cursor):
    # check that column is valid
    if column not in userListColumns:
        print(f'no column named "{column}" in user_list table')
        return
    # column is valid, update info
    try:
        serverID = server.id
        tableName = f"user_list_{serverID}"
        userID = member.id
        update = f"""
        UPDATE {tableName}
        SET {column} = '{newInfo}'
        WHERE user_id = {userID}
        """
        cursor.execute(update)
        print(f"user {member.name}'s {column} set to {newInfo} in user_list table")

    except Exception as error:
        print(error)

    return


# update an entire column of the user_list table at once
# server arg is an instance of discord.Guild
def ulUpdateColumn(column, newInfoList, server, cursor):
    # check that column is valid
    if column not in userListColumns:
        print(f'no column named "{column}" in user_list table')
        return
    # column is valid, update info
    try:
        serverID = server.id
        tableName = f"user_list_{serverID}"
        # grab list of userID's
        uidList = ulGetUIDList(server, cursor)
        if uidList != None:
            i = 0
            while i < len(uidList) and i < len(newInfoList):
                update = f"""
                UPDATE {tableName}
                SET {column} = '{newInfoList[i]}'
                WHERE user_id = {uidList[i]}
                """
                cursor.execute(update)
                i += 1
            print(f"{column} column updated in user_list table")

    except Exception as error:
        print(error)

    return


# updates a user's name in the user_list table
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
# newName is last argument to match syntax of updateName,
# where newName is an optional arg with default value None
def ulUpdateName(server, member, cursor, newName):
    return ulUpdate("name", newName, server, member, cursor)


# updates a user's pronouns in the user_list table
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
def ulUpdatePronouns(server, member, cursor, newPro):
    return ulUpdate("pronouns", newPro, server, member, cursor)


# updates a user's nickname in the user_list table
# pulls nickname from the server
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
def ulUpdateNickname(server, member, cursor):
    return ulUpdate("nickname", member.nick, server, member, cursor)


# update the name column of the user_list table
# server arg is an instance of discord.Guild
def ulUpdateNameCol(newNames, server, cursor):
    return ulUpdateColumn("name", newNames, server, cursor)

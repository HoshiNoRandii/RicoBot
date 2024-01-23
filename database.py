### database access functions

# columns in the user_list table
userListColumns = ["user_id", "username", "name", "pronouns", "nickname", "dev_flag"]


# get functions


# gets a user's info from the selected column
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
def dbGet(column, server, member, cursor):
    # check that column is valid
    if column not in userListColumns:
        print(f'no column named "{column}" in user_list table')
        return
    # column is valid, grab info
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
    return ret


# fetches an entire column from the user_list table
# server arg is an instance of discord.Guild
def dbGetList(column, server, cursor):
    # check that column is valid
    if column not in userListColumns:
        print(f'no column named "{column}" in user_list table')
        return
    # column is valid, grab info
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
def dbGetName(server, member, cursor):
    return dbGet("name", server, member, cursor)


# gets a user's pronouns from the database
# server arg is an instance or discord.Guild
# member arg is an instance of discord.Member
def dbGetPronouns(server, member, cursor):
    return dbGet("pronouns", server, member, cursor)


# gets a user's dev status from the database
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
def dbGetDevFlag(server, member, cursor):
    return dbGet("dev_flag", server, member, cursor)


# gets the list of all user id's in the database
# server arg is an instance of discord.Guild
def dbGetUIDList(server, cursor):
    return dbGetList("user_id", server, cursor)


# gets the list of all names in the database
# server arg is an instance of discord.Guild
def dbGetNameList(server, cursor):
    return dbGetList("name", server, cursor)


# gets the list of all the pronoun sets
# in the database
# server arg is an instance of discord.Guild
def dbGetPronounList(server, cursor):
    return dbGetList("pronouns", server, cursor)


# update functions


# udpate a user's info in the database in the selected column
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
def dbUpdate(column, newInfo, server, member, cursor):
    # check that column is valid
    if column not in userListColumns:
        print(f'no column named "{column}" in user_list table')
        return
    # column is valid, update info
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
    return


# update an entire column of the user_list table at once
# server arg is an instance of discord.Guild
def dbUpdateColumn(column, newInfoList, server, cursor):
    # check that column is valid
    if column not in userListColumns:
        print(f'no column named "{column}" in user_list table')
        return
    # column is valid, update info
    serverID = server.id
    tableName = f"user_list_{serverID}"
    # grab list of userID's
    uidList = dbGetUIDList(server, cursor)
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
    return


# updates a user's name in the user_list table
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
# newName is last argument to match syntax of updateName,
# where newName is an optional arg with default value None
def dbUpdateName(server, member, cursor, newName):
    return dbUpdate("name", newName, server, member, cursor)


# updates a user's pronouns in the user_list table
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
def dbUpdatePronouns(server, member, cursor, newPro):
    return dbUpdate("pronouns", newPro, server, member, cursor)


# updates a user's nickname in the user_list table
# pulls nickname from the server
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
def dbUpdateNickname(server, member, cursor):
    return dbUpdate("nickname", member.nick, server, member, cursor)


# update the name column of the user_list table
# server arg is an instance of discord.Guild
def dbUpdateNameCol(newNames, server, cursor):
    return dbUpdateColumn("name", newNames, server, cursor)

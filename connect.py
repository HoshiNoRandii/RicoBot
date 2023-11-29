### Create the connection pool in order to access
### the postgres database
### and database access functions

import psycopg2
from psycopg2 import pool
import inspect
from functools import wraps

from config import config


# init: create the global connPool
def init():
    global connPool
    print("Attempting to create postgres connection pool...")
    connPool = connectPool()
    while connPool == None:
        print("Retrying...")
        connPool = connectPool()
    return


# connectPool: create the connection pool
def connectPool():
    try:
        # read connection parameters
        params = config()

        # create the pool
        connPool = pool.SimpleConnectionPool(1, 20, **params)

        if connPool:
            print("Connection pool created successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating postgres connection pool:", error)
        return None

    return connPool


# closePool(connPool): close the connection pool connPool
def closePool(connPool):
    connPool._closeall()
    print("Connection pool is closed")
    return


# decorator function for commands that will access the
# postgres database and take no arguments
# any function wrapped with db_connector_no_args must have
# cursor as a keyword only argument
# and also must be an async function
def db_connector_no_args(func):
    # wrapper function
    @wraps(func)
    async def inner(*args, **kwargs):
        print(
            f"Attempting to connect to the postgres database to execute {func.__name__}"
        )
        psConn = None
        try:
            # get a connection to the postgres db from the
            # connection pool
            psConn = connPool.getconn()

            if psConn:
                print("Successfully retrieved postgres connection from connection pool")
                # open cursor
                psCursor = psConn.cursor()

                # add this cursor to the kwargs
                if "cursor" in inspect.getfullargspec(func).kwonlyargs:
                    kwargs["cursor"] = psCursor

                # execute the function with the cursor
                await func(*args, **kwargs)

                # close cursor
                psCursor.close()

                # commit changes
                psConn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            if psConn is not None:
                # put away the connection
                connPool.putconn(psConn)
                print("Successfully put away the postgres connection")

        return

    return inner


# decorator function for commands that will access the
# postgres database and take arguments
# any function wrapped with db_connector_with_args must have
# (self, ctx) as the first two arguments and
# cursor as a keyword only argument
# and also must be an async function
def db_connector_with_args(func):
    # wrapper function
    @wraps(func)
    async def inner(self, ctx, *args, **kwargs):
        print(
            f"Attempting to connect to the postgres database to execute {func.__name__}"
        )
        psConn = None
        try:
            # get a connection to the postgres db from the
            # connection pool
            psConn = connPool.getconn()

            if psConn:
                print("Successfully retrieved postgres connection from connection pool")
                # open cursor
                psCursor = psConn.cursor()

                # add this cursor to the kwargs
                if "cursor" in inspect.getfullargspec(func).kwonlyargs:
                    kwargs["cursor"] = psCursor

                # execute the function with the cursor
                await func(self, ctx, *args, **kwargs)

                # close cursor
                psCursor.close()

                # commit changes
                psConn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            if psConn is not None:
                # put away the connection
                connPool.putconn(psConn)
                print("Successfully put away the postgres connection")

        return

    return inner


## database access functions ##

# columns in the user_list table
userListColumns = ["user_id", "username", "name", "pronouns", "nickname"]


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


# updates a user's name in the user_list table
# server arg is an instance of discord.Guild
# member arg is an instance of discord.Member
# newName is last argument to match syntax of updateNameRole,
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

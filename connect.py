### Create the connection pool in order to access
### the postgres database

import psycopg2
from psycopg2 import pool
import inspect

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

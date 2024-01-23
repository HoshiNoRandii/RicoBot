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
    # read connection parameters
    params = config()

    # create connection pool
    global connPool
    print("Attempting to create postgres connection pool...")
    connPool = connectPool(params)
    while connPool == None:
        print("Retrying...")
        connPool = connectPool(params)
    return


# connectPool: create the connection pool
# params arg is a dict with the connection parameters
def connectPool(params):
    try:
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
        conn = None
        try:
            # get a connection to the postgres db from the
            # connection pool
            conn = connPool.getconn()

            if conn:
                print("Successfully retrieved postgres connection from connection pool")
                # open cursor
                cursor = conn.cursor()

                # add this cursor to the kwargs
                if "cursor" in inspect.getfullargspec(func).kwonlyargs:
                    kwargs["cursor"] = cursor

                # execute the function with the cursor
                await func(*args, **kwargs)

                # close cursor
                cursor.close()

                # commit changes
                conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            if conn is not None:
                # put away the connection
                connPool.putconn(conn)
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
        conn = None
        try:
            # get a connection to the postgres db from the
            # connection pool
            conn = connPool.getconn()

            if conn:
                print("Successfully retrieved postgres connection from connection pool")
                # open cursor
                cursor = conn.cursor()

                # add this cursor to the kwargs
                if "cursor" in inspect.getfullargspec(func).kwonlyargs:
                    kwargs["cursor"] = cursor

                # execute the function with the cursor
                await func(self, ctx, *args, **kwargs)

                # close cursor
                cursor.close()

                # commit changes
                conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            if conn is not None:
                # put away the connection
                connPool.putconn(conn)
                print("Successfully put away the postgres connection")

        return

    return inner

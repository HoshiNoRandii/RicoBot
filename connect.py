### Create the connection pool in order to access
### the postgres database
### and database access functions

import psycopg2
from psycopg2 import pool
import inspect
from functools import wraps

from config import config


def init():
    """
    Create the global connection pool connPool

    connPool: psycopg2.pool.SimpleConnectionPool

    returns: none
    """
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


def connectPool(params):
    """
    Create a connection pool

    args:
       params: dict

    returns: psycopg2.pool.SimpleConnectionPool | None
    """
    try:
        # create the pool
        connPool = pool.SimpleConnectionPool(1, 20, **params)

        if connPool:
            print("Connection pool created successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating postgres connection pool:", error)
        return None

    return connPool


def closePool(pool=connPool):
    """
    Close a connection pool

    args:
        pool: psycopg2.pool.SimpleConnectionPool | None
            default argument is the global connPool

    returns: None
    """
    if pool != None:
        pool.closeall()
        print("Connection pool is closed")
    return


def db_connector_no_args(func):
    """
    Decorator function for commands that will access the postgres database and take no arguments

    Any function wrapped with db_connector_no_args must:
        - have "cursor" as a keyword only argument
        - be an async function.
    """

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


def db_connector_with_args(func):
    """
    Decorator function for commands that will access the postgres database and take arguments

    Any function wrapped with db_connector_with_args must:
        - have (self, ctx) as the first two arguments
        - have cursor as a keyword only argument
        - be an async function
    """

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

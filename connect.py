### Create the connection pool in order to access
### the postgres database

import psycopg2
from psycopg2 import pool
import inspect

from config import config


# init: create the global connPool
def init():
    global connPool
    connPool = connectPool()


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


# decorator function for all commands that will access the
# postgres databas
# any function wrapped with db_connector must have
# cursor as an argument
def db_connector(func):
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
                if "cursor" in inspect.getfullargspec(func).args:
                    kwargs["cursor"] = psCursor

                # execute the function with the cursor
                func(*args, **kwargs)

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

### Create the connection pool in order to access
### the postgres database

import psycopg2
from psycopg2 import pool
from config import config

# init: create the global connPool
# and close it (for now)
def init():
    global connPool
    connPool = connectPool()
    if connPool:
        closePool(connPool)

# connectPool: create the connection pool
def connectPool():
    try:
        # read connection parameters
        params = config()

        # create the pool
        connPool = psycopg2.pool.AbstractConnectionPool(1, 20, **params)

        if connPool:
            print("Connection pool created successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating postgres connection pool", error)
        return None

    return connPool

# closePool(connPool): close the connection pool connPool
def closePool(connPool):
    connPool._closeall()
    print("Connection pool is closed")
    return

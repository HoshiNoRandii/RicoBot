### Create the connection pool in order to access
### the postgres database

import psycopg2
from config import config

# connectPool: create the connection pool
def connectPool():
    try:
        # read connection parameters
        params = config()

        # create the pool
        pool = psycopg2.pool.AbstractConnectionPool(1, 20, **params)

        if pool:
            print("Connection pool created successfully")

    except (Exception, psycop2.DatabaseError) as error:
        print("Error while creating postgres connection pool", error)

    return pool

# closePool(pool): close the connection pool pool
def closePool(pool):
    pool.closeall
    print("Connection pool is closed")
    return

import sqlite3
import pymysql
import psycopg2




DB_TYPE = "sqlite"

DB_CONFIG = {
    "sqlite": {
        "path": "Chinook_Sqlite.sqlite"
    },

    "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "test"
    },

    "postgres": {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "",
        "database": "test"
    }
}




def set_database(db_type, **kwargs):
    global DB_TYPE

    DB_TYPE = db_type

    if db_type == "sqlite":
        DB_CONFIG["sqlite"]["path"] = kwargs["path"]

    elif db_type == "mysql":
        DB_CONFIG["mysql"].update(kwargs)

    elif db_type == "postgres":
        DB_CONFIG["postgres"].update(kwargs)




def get_connection():

    if DB_TYPE == "sqlite":

        return sqlite3.connect(
            DB_CONFIG["sqlite"]["path"]
        )

    elif DB_TYPE == "mysql":

        return pymysql.connect(
            host=DB_CONFIG["mysql"]["host"],
            port=int(DB_CONFIG["mysql"]["port"]),
            user=DB_CONFIG["mysql"]["user"],
            password=DB_CONFIG["mysql"]["password"],
            database=DB_CONFIG["mysql"]["database"]
        )

    elif DB_TYPE == "postgres":

        return psycopg2.connect(
            host=DB_CONFIG["postgres"]["host"],
            port=DB_CONFIG["postgres"]["port"],
            user=DB_CONFIG["postgres"]["user"],
            password=DB_CONFIG["postgres"]["password"],
            dbname=DB_CONFIG["postgres"]["database"]
        )

    else:
        raise ValueError(f"Unsupported database type: {DB_TYPE}")



def execute_query(query):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [
            col[0]
            for col in cursor.description
        ]

        return columns, rows

    finally:

        conn.close()





def get_db_type():
    return DB_TYPE
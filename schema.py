from db import get_connection, get_db_type


def get_schema():

    conn = get_connection()
    cursor = conn.cursor()

    db_type = get_db_type()

    schema = f"Database type: {db_type}\n\n"

    # ======================================================
    # SQLITE
    # ======================================================
    if db_type == "sqlite":

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
        """)

        tables = cursor.fetchall()

        for table in tables:

            table_name = table[0]

            # skip sqlite internal tables
            if table_name.startswith("sqlite_"):
                continue

            schema += f"Table: {table_name}\n"

            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            for col in columns:
                # col = (cid, name, type, notnull, default_value, pk)
                schema += f"- {col[1]} ({col[2]})\n"

            schema += "\n"


    # ======================================================
    # MYSQL
    # ======================================================
    elif db_type == "mysql":

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
        """)

        tables = cursor.fetchall()

        for table in tables:

            table_name = table[0]

            schema += f"Table: {table_name}\n"

            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                AND table_schema = DATABASE()
            """)

            columns = cursor.fetchall()

            for col in columns:
                schema += f"- {col[0]} ({col[1]})\n"

            schema += "\n"


    # ======================================================
    # POSTGRESQL
    # ======================================================
    elif db_type == "postgres":

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
        """)

        tables = cursor.fetchall()

        for table in tables:

            table_name = table[0]

            schema += f"Table: {table_name}\n"

            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                AND table_schema = 'public'
            """)

            columns = cursor.fetchall()

            for col in columns:
                schema += f"- {col[0]} ({col[1]})\n"

            schema += "\n"


    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    conn.close()

    return schema
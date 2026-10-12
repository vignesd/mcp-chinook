import sqlite3


def get_database_schema(db_file="data/chinook.db"):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Query to get all table names and their creation SQL
    query = """
    SELECT name, sql 
    FROM sqlite_master 
    WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """

    cursor.execute(query)
    tables = cursor.fetchall()

    # Print the schema for each table
    for table_name, schema_sql in tables:
        print(f"--- Table: {table_name} ---")
        print(schema_sql)
        print("\n")

    conn.close()


if __name__ == "__main__":
    get_database_schema()

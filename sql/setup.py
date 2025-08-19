from utils import get_snowflake_connection


def setup_snowflake(commands_file: str = 'setup.sql') -> None:
    """
    Run the SQL setup file (setup.sql) to create all tables, warehouse,
    and insert initial data.

    The function opens the file, splits by semicolons, and executes
    each SQL statement in Snowflake.
    """
    conn = get_snowflake_connection(initial=True)
    cursor = conn.cursor()

    with open(commands_file, 'r') as file:
        sql_commands = file.read()

    # split by ; so we can execute multiple commands
    sql_commands = sql_commands.split(';')
    for command in sql_commands:
        if command.strip():
            cursor.execute(command)

    cursor.close()
    conn.close()
    print("✅ Snowflake setup complete.")

if __name__ == "__main__":
    setup_snowflake()
    print("Setup completed successfully.")
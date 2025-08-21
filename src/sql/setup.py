from src.utils import get_snowflake_connection


def setup_snowflake(commands_file: str = 'setup.sql') -> None:
    """
    Runs the SQL setup file to create tables, warehouse,
    and insert initial data in Snowflake
    """
    conn = get_snowflake_connection(initial=True)
    cursor = conn.cursor()

    # read sql commands from file
    with open(commands_file, 'r') as file:
        sql_commands = file.read()

    # split by ; to execute multiple commands
    sql_commands = sql_commands.split(';')
    for command in sql_commands:
        if command.strip():
            cursor.execute(command)

    cursor.close()
    conn.close()
    print("Snowflake setup complete.")


if __name__ == "__main__":
    setup_snowflake()
    print("Setup completed successfully.")

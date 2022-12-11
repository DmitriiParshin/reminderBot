import sqlite3


class SQLiteClient:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.connect = None

    def create_connection(self):
        self.connection = sqlite3.connect(
            self.filepath,
            check_same_thread=False
        )

    def close_connection(self):
        self.connection.close()

    def execute_command(self, command: str, params: tuple):
        if self.connection is not None:
            self.connection.execute(command, params)
            self.connection.commit()
        else:
            raise ConnectionError("You need to create connection to database!")

    def execute_select_command(self, command: str):
        if self.connection is not None:
            cursor = self.connection.cursor()
            cursor.execute(command)
            return cursor.fetchall()
        else:
            raise ConnectionError("You need to create connection to database!")

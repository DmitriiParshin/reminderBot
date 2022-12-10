import sqlite3


class SQLiteClient:
    def __init__(self, filepath):
        self.filepath = filepath
        self.connection = None

    def create_connection(self):
        self.connection = sqlite3.connect(
            self.filepath,
            check_same_thread=False
        )

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


class UserManager:
    CREATE_USER = """
        INSERT INTO users (user_id, username, chat_id) VALUES (?, ?, ?);
        """

    GET_USER = """
    SELECT user_id, username, chat_id FROM users WHERE user_id = %s;
    """

    def __init__(self, database_client: SQLiteClient):
        self.database_client = database_client

    def setup(self):
        self.database_client.create_connection()

    def get_user(self, user_id: str):
        user = self.database_client.execute_select_command(
            self.GET_USER % user_id
        )
        return user[0] if user else user

    def create_user(self, user_id: str, username: str, chat_id: int):
        self.database_client.execute_command(
            self.CREATE_USER,
            (user_id, username, chat_id)
        )

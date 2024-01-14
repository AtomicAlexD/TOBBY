import pyodbc

db_connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=master;trusted_connection=yes;'
conn = pyodbc.connect(db_connection_string)

class db_calls:
    def __init__(self) -> None:
        pass
    
    def __enter__(self):
        self.cursor = conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()

class db_read(db_calls):
    def db_read_multiple_lines(self,procedure):
        with self:
            self.cursor.execute(procedure)
            data = self.cursor.fetchall()
        return data

    def add_category(self, guild_id: int, category_name: str, category_description: str) -> str:
        """
        This function will add a category to the database.

        :param guild_id: The ID of the guild where the category should be added.
        :param category_name: The name of the category that should be added.

        """
        self.cursor.execute('INSERT INTO categories(guild_id, category_name, category_description) VALUES (?, ?, ?)',
            (guild_id, category_name, category_description),
        )
        self.connection.commit()
        self.connection.execute('SELECT TOP (1) category_name FROM categories WHERE guild_id=? ORDER BY id DESC',(guild_id))
        new_category = self.cursor.fetchone()
        return new_category


    async def add_item_to_rate(
        self, guild_id: int, category_name: str, item_name: str, description: str
    ) -> None:
        """
        This function will add an item to rate to the database.

        :param guild_id: The ID of the guild where the item should be added.
        :param category_name: The name of the category where the item should be added.
        :param item_name: The name of the item that should be added.
        """
        await self.connection.execute(
            "INSERT INTO items_to_rate(guild_id, category_name, item_name, description) VALUES (?, ?, ?, ?)",
            (
                guild_id,
                category_name,
                item_name,
                description,
            ),
        )
        await self.connection.commit()

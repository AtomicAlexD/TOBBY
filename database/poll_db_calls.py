import pyodbc


class db_calls:
    def __init__(self) -> None:
        self.db_connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=tobby;trusted_connection=yes;'
        self.conn = pyodbc.connect(self.db_connection_string)
        self.cursor = self.conn.cursor()

class db_read(db_calls):
    def __init__(self) -> None:
        super().__init__()
    
    def get_categories(self, guild_id: int) -> list:
        try:
            self.cursor.execute('SELECT category_name, category_description FROM categories WHERE guild_id=?', (guild_id))
            categories = self.cursor.fetchall()
            return categories
        except Exception as e:
            print(e)
            return None
        
class db_write(db_calls):
    def __init__(self) -> None:
        super().__init__()

    def add_category(self, guild_id: int, category_name: str, category_description: str) -> str:
        try:
            self.cursor.execute('INSERT INTO categories(guild_id, category_name, category_description) VALUES (?, ?, ?)',
                (guild_id, category_name, category_description),
            )
            self.cursor.commit()
            self.cursor.execute('SELECT TOP (1) category_name FROM categories WHERE guild_id=? ORDER BY id DESC',(guild_id))
            new_category = self.cursor.fetchone()
            return new_category[0]
        except Exception as e:
            print(e)
            return None
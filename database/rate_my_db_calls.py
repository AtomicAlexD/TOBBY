import pyodbc


class db_calls:
    def __init__(self) -> None:
        self.db_connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=rate_my;trusted_connection=yes;'
        self.conn = pyodbc.connect(self.db_connection_string)
        self.cursor = self.conn.cursor()

    # def __enter__(self):
    #     self.connection = pyodbc.connect(db_connection_string.value)
    #     self.cursor = self.connection.cursor()
    #     return self
    
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     if exc_type is not None:
    #         self.cursor.rollback()
    #     else:
    #         self.cursor.commit()
    #     self.cursor.close()
    #     self.connection.close()

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

    def get_items_to_rate(self, user_id: str, guild_id: str) -> list:
        #print(f'user_id: {user_id}, guild_id: {guild_id}')
        # get a list of items that have not been rated by the user and are available to rate (based on date) for the guild
        try:
            self.cursor.execute('''SELECT itr.name
    ,c.category_name
    ,itr.[description]
    ,itr.available_to_rate_date
FROM dbo.items_to_rate AS itr
INNER JOIN dbo.categories AS c 
    ON itr.category_id = c.id
LEFT OUTER JOIN dbo.ratings AS r 
    ON itr.id = r.item_id
    AND r.user_id = ?
WHERE itr.guild_id = ?
    AND r.id IS NULL
    AND itr.available_to_rate_date < GETDATE()''', (user_id,guild_id))
            items = self.cursor.fetchall()
            return items
        except Exception as e:
            print(e)
            return 'error'
    
    def view_my_ratings(self, user_id: str, guild_id: str) -> list:
        try:
            self.cursor.execute('''SELECT itr.name
    ,c.category_name
    ,itr.[description]
    ,r.rating
FROM dbo.items_to_rate AS itr
INNER JOIN dbo.categories AS c 
    ON itr.category_id = c.id
INNER JOIN dbo.ratings AS r
    ON itr.id = r.item_id
WHERE itr.guild_id = ?
    AND r.user_id = ?''', (guild_id,user_id))
            items = self.cursor.fetchall()
            return items
        except Exception as e:
            print(e)
            return 'error'
        

class db_write(db_calls):
    def __init__(self) -> None:
        super().__init__()

    def add_category(self, guild_id: int, category_name: str, category_description: str) -> str:
        #print(f'guild_id: {guild_id}, category_name: {category_name}, category_description: {category_description}')
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
    

    def add_item_to_rate(
        self, guild_id: str, item_name: str, category_name: str, description: str, available_to_rate_date: str
    ) -> str:
        try:
            sql = 'SELECT id FROM dbo.categories WHERE guild_id=? AND category_name=?'
            self.cursor.execute(sql, (guild_id, category_name))
            category_id = self.cursor.fetchone()
            if category_id is None:
                return 'no category found'
            cat_id = category_id[0]
        except Exception as e:
            print(e)
            return 'no category found'
        print(cat_id)
        try:
            self.cursor.execute(
                "INSERT INTO items_to_rate(guild_id, name, category_id, description, available_to_rate_date) VALUES (?, ?, ?, ?, ?)",
                (
                    guild_id,
                    item_name,
                    cat_id,
                    description,
                    available_to_rate_date
                ),
            )
            self.cursor.commit()
        except Exception as e:
            print(e)
            return 'could not add item to rate'
        return 'item added to rate'

    def rate_item(self, guild_id: str, user_id: str, item_id: int, rating: int) -> None:
        try:
            self.cursor.execute(
                "INSERT INTO ratings(guild_id, item_id, user_id, rating) VALUES (?, ?, ?, ?)",
                (
                    guild_id,
                    item_id,
                    user_id,
                    rating
                ),
            )
            self.cursor.commit()
        except Exception as e:
            print(e)
            return 'could not add rating'
        return 'rating added'

import pyodbc

class db_calls:
    def __init__(self) -> None:
        self.db_connection_string = "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=tobby;trusted_connection=yes;"
        self.conn = pyodbc.connect(self.db_connection_string)
        self.cursor = self.conn.cursor()

class db_read(db_calls):
    def __init__(self) -> None:
        super().__init__()

    def get_categories(self, guild_id: int) -> list:
        try:
            sql = """SELECT rc.[name]
            ,rc.[description]
            ,count(rm.id) AS metric_count
            FROM ratings.category AS rc
            INNER JOIN ratings.metric AS rm
                ON rc.id = rm.category_id
            WHERE guild_id=?
            GROUP BY rc.[name], rc.[description]"""
            self.cursor.execute(sql,(guild_id))
            categories = self.cursor.fetchall()
            return categories
        except Exception as e:
            print(e)
            return None

    def get_most_recent_item(self, guild_id: int) -> str:
        try:
            sql = """SELECT TOP (1) ri.[name]
FROM ratings.item AS ri
INNER JOIN ratings.category AS rc
    ON ri.category_id = rc.id
WHERE rc.guild_id = ?
AND ri.available_to_rate_date < GETDATE()
ORDER BY ri.available_to_rate_date DESC"""
            self.cursor.execute(sql, (guild_id))
            item = self.cursor.fetchone()
            return item[0]
        except Exception as e:
            print(e)
            return None

    def check_user_has_rated_item(
        self, guild_id: str, user_id: str, item_name: str, metric_name: str
    ) -> bool:
        try:
            self.cursor.execute(
                """SELECT rr.id
                FROM ratings.rating AS rr
                INNER JOIN ratings.item AS ri
                    ON rr.item_id = ri.id
                INNER JOIN ratings.category AS rc
                    ON ri.category_id = rc.id
                INNER JOIN ratings.metric AS rm
                    ON rr.metric_id = rm.id
                WHERE rc.guild_id=? 
                    AND ri.name=? 
                    AND r.user_id=?
                    AND rm.name=?
                """,
                (guild_id, item_name, user_id, metric_name),
            )
            rating = self.cursor.fetchone()
            if rating is None:
                return False
            else:
                return True
        except Exception as e:
            print(e)
            return False

    def get_items_to_rate(self, user_id: str, guild_id: str) -> list:
        # get a list of items that have not been rated by the user and are available to rate (based on date) for the guild
        try:
            self.cursor.execute(
                """SELECT ri.name
    ,rc.[name]
    ,ri.[description]
    ,ri.available_to_rate_date
FROM ratings.item AS ri
INNER JOIN ratings.category AS rc 
    ON ri.category_id = rc.id
LEFT OUTER JOIN ratings.rating AS rr 
    ON ri.id = rr.item_id
    AND rr.user_id = ?
WHERE rc.guild_id = ?
    AND rr.id IS NULL
    AND ri.available_to_rate_date < GETDATE()""",
                (user_id, guild_id),
            )
            items = self.cursor.fetchall()
            return items
        except Exception as e:
            print(e)
            return "error"

    def view_my_ratings(self, user_id: str, guild_id: str) -> list:
        try:
            self.cursor.execute(
                """SELECT ri.name
    ,rc.[name]
    ,ri.[description]
    ,AVG(r.rating)
FROM ratings.item AS ri
INNER JOIN ratings.category AS rc 
    ON ri.category_id = rc.id
INNER JOIN ratings.rating AS r
    ON ri.id = r.item_id
WHERE rc.guild_id = ?
    AND r.user_id = ?
GROUP BY ri.name, rc.[name], ri.[description]""",
                (guild_id, user_id),
            )
            items = self.cursor.fetchall()
            return items
        except Exception as e:
            print(e)
            return "error"

    def view_ratings(self, guild_id: str, item_name: str) -> list:
        try:
            self.cursor.execute(
                """SELECT rm.name, AVG(r.rating) AS average_rating
                FROM ratings.rating AS r
                INNER JOIN ratings.metric AS rm
                    ON r.metric_id = rm.id
                INNER JOIN ratings.item AS ri
                    ON r.item_id = ri.id
                INNER JOIN ratings.category AS rc
                    ON ri.category_id = rc.id
                WHERE rc.guild_id=? AND ri.name=?
                GROUP BY rm.name""",
                (guild_id, item_name),
            )
            ratings = self.cursor.fetchall()
            return ratings
        except Exception as e:
            print(e)
            return "could not get ratings"

    def view_items_by_category(self, guild_id: str, category_name: str) -> list:
        try:
            self.cursor.execute(
                """SELECT ri.name
                    ,ri.description
                    ,ri.available_to_rate_date
                    ,AVG(r.rating) AS average_rating
                FROM ratings.item AS ri
                INNER JOIN ratings.category AS c
                    ON ri.category_id = c.id
                LEFT OUTER JOIN ratings.rating AS r
                    ON ri.id = r.item_id
                WHERE c.guild_id=? AND c.[name]=?
                GROUP BY ri.name, ri.description, ri.available_to_rate_date""",
                (guild_id, category_name),
            )
            items = self.cursor.fetchall()
            return items
        except Exception as e:
            print(e)
            return "could not get items"

    def get_metrics(self, guild_id: str, category_name: str) -> list:
        try:
            self.cursor.execute(
                """SELECT rm.name
                    ,rm.description
                    ,rm.id
                FROM ratings.metric AS rm
                INNER JOIN ratings.category AS rc
                    ON rm.category_id = rc.id
                WHERE rc.guild_id=? AND rc.name=?""",
                (guild_id, category_name),
            )
            metrics = self.cursor.fetchall()
            return metrics
        except Exception as e:
            print(e)
            return "could not get metrics"
        
    def get_category_id(self, guild_id: str, category_name: str) -> int:
        try:
            self.cursor.execute(
                """SELECT id
                FROM ratings.category
                WHERE guild_id=? AND [name]=?""",
                (guild_id, category_name),
            )
            category_id = self.cursor.fetchone()
            return category_id[0]
        except Exception as e:
            print(e)
            return "could not get category id"

    def get_category_id_of_item(self, guild_id: str, item_name: str) -> int:
        try:
            self.cursor.execute(
                """SELECT rc.id
                FROM ratings.item AS ri
                INNER JOIN ratings.category AS rc
                    ON ri.category_id = rc.id
                WHERE rc.guild_id=? AND ri.name=?""",
                (guild_id, item_name),
            )
            category_id = self.cursor.fetchone()
            return category_id[0]
        except Exception as e:
            print(e)
            return "could not get category id"
        
    def get_metrics_for_item(self, guild_id: str, category_id: int) -> list:
        try:
            self.cursor.execute(
                """SELECT rm.name
                    ,rm.description
                    ,rm.id
                FROM ratings.metric AS rm
                INNER JOIN ratings.category AS rc
                    ON rm.category_id = rc.id
                WHERE rc.guild_id=? AND rc.id=?""",
                (guild_id, category_id),
            )
            metrics = self.cursor.fetchall()
            return metrics
        except Exception as e:
            print(e)
            return "could not get metrics"
        
    def get_user_ratings_for_item(self, guild_id: str, user_id: str, item_name: str) -> list:
        try:
            self.cursor.execute(
                """SELECT rm.name, r.rating
                FROM ratings.rating AS r
                INNER JOIN ratings.item AS ri
                    ON r.item_id = ri.id
                INNER JOIN ratings.category AS rc
                    ON ri.category_id = rc.id
                INNER JOIN ratings.metric AS rm
                    ON r.metric_id = rm.id
                WHERE rc.guild_id=? AND ri.name=? AND r.user_id=?""",
                (guild_id, item_name, user_id),
            )
            ratings = self.cursor.fetchall()
            return ratings
        except Exception as e:
            print(e)
            return "could not get ratings"

    def get_previous_rating(self, guild_id: str, user_id: str, item_name: str, metric_name: str) -> int:
        try:
            self.cursor.execute(
                """SELECT r.rating
                FROM ratings.rating AS r
                INNER JOIN ratings.item AS ri
                    ON r.item_id = ri.id
                INNER JOIN ratings.category AS rc
                    ON ri.category_id = rc.id
                INNER JOIN ratings.metric AS rm
                    ON r.metric_id = rm.id
                WHERE rc.guild_id=? AND ri.name=? AND r.user_id=? AND rm.name=?""",
                (guild_id, item_name, user_id, metric_name),
            )
            rating = self.cursor.fetchone()
            return rating[0]
        except Exception as e:
            print(e)
            return "could not get previous rating"
        
    def check_item_availability(self):
        sql = '''SELECT TOP (1) i.name, c.announcement_channel_id, i.id, i.description
FROM tobby.ratings.item AS i
INNER JOIN tobby.ratings.category AS c
    ON i.category_id = c.id
WHERE i.available_to_rate_date < GETDATE()
    AND i.announced = 0
    AND c.announcement_channel_id IS NOT NULL
ORDER BY i.available_to_rate_date DESC'''
        try:
            self.cursor.execute(sql)
            item = self.cursor.fetchone()
            if item is None:
                return None, None, None, None
            return item
        except Exception as e:
            print(e)
            return None

class db_write(db_calls):
    def __init__(self) -> None:
        super().__init__()

    def add_metric(
        self, category_id: int, metric_name: str, metric_description: str
    ) -> str:
        try:
            self.cursor.execute(
                "INSERT INTO ratings.metric(category_id, [name], description) VALUES (?, TRIM(?), ?)",
                (category_id, metric_name, metric_description),
            )
            self.cursor.commit()
            self.cursor.execute(
                "SELECT TOP (1) [name],id FROM ratings.metric WHERE category_id=? ORDER BY id DESC",
                (category_id),
            )
            new_metric = self.cursor.fetchone()
            new_metric_name = new_metric[0]
            return new_metric_name
        except Exception as e:
            print(e)
            return None

    def add_category(
        self, guild_id: int, category_name: str, category_description: str
    ) -> str:
        try:
            self.cursor.execute(
                "INSERT INTO ratings.category(guild_id, [name], description) VALUES (?, ?, ?)",
                (guild_id, category_name, category_description),
            )
            self.cursor.commit()
            self.cursor.execute(
                "SELECT TOP (1) [name],id FROM ratings.category WHERE guild_id=? ORDER BY id DESC",
                (guild_id),
            )
            new_category = self.cursor.fetchone()
            new_category_name = new_category[0]
            new_category_id = new_category[1]
            new_metric = self.add_metric(new_category_id, "overall", 'The "overall rating" for this item')
            return new_category_name, new_metric, new_category_id
        except Exception as e:
            print(e)
            return None

    def add_item_to_rate(
        self,
        guild_id: str,
        item_name: str,
        category_name: str,
        description: str,
        available_to_rate_date: str,
    ) -> str:
        try:
            sql = "SELECT id FROM ratings.category WHERE guild_id=? AND [name]=?"
            self.cursor.execute(sql, (guild_id, category_name))
            category_id = self.cursor.fetchone()
            if category_id is None:
                return "no category found"
            cat_id = category_id[0]
        except Exception as e:
            print(e)
            return "no category found"
        print(cat_id)
        try:
            self.cursor.execute(
                "INSERT INTO ratings.item(name, category_id, description, available_to_rate_date) VALUES (?, ?, ?, ?)",
                (item_name, cat_id, description, available_to_rate_date),
            )
            self.cursor.commit()
        except Exception as e:
            print(e)
            return "could not add item to rate"
        return "item added to rate"

    def rate_item(
        self, guild_id: str, user_id: str, item_name: str, rating: int, metric_name: str
    ) -> None:
        try:
            self.cursor.execute(
                """SELECT ri.id 
                FROM ratings.item AS ri 
                INNER JOIN ratings.category AS rc 
                    ON ri.category_id = rc.id 
                WHERE rc.guild_id=? 
                    AND ri.name=?""",
                (guild_id, item_name),
            )
            item_id = self.cursor.fetchone()
            self.cursor.execute(
                """SELECT rm.id 
                FROM ratings.metric AS rm 
                INNER JOIN ratings.category AS rc 
                    ON rm.category_id = rc.id 
                WHERE rc.guild_id=?
                    AND rm.name=?""",
                (guild_id, metric_name),
            )
            metric_id = self.cursor.fetchone()
            self.cursor.execute(
                "INSERT INTO ratings.rating(metric_id, item_id, user_id, rating) VALUES (?, ?, ?, ?)",
                (metric_id[0],item_id[0], user_id, rating),
            )
            self.cursor.commit()
        except Exception as e:
            print(e)
            return "could not add rating"
        return "rating added"

    def update_item_rating(
        self, guild_id: str, user_id: str, item_name: str, rating: int, metric_name: str
    ) -> None:
        try:
            self.cursor.execute(
                """SELECT ri.id 
                FROM ratings.item AS ri 
                INNER JOIN ratings.category AS rc 
                    ON ri.category_id = rc.id 
                WHERE rc.guild_id=? 
                    AND ri.name=?""",
                (guild_id, item_name),
            )
            item_id = self.cursor.fetchone()
            self.cursor.execute(
                """SELECT rm.id 
                FROM ratings.metric AS rm 
                INNER JOIN ratings.category AS rc 
                    ON rm.category_id = rc.id 
                WHERE rc.guild_id=?
                    AND rm.name=?""",
                (guild_id, metric_name),
            )
            metric_id = self.cursor.fetchone()
            self.cursor.execute(
                """UPDATE ratings.rating
                set rating=?
                WHERE metric_id=? AND item_id=? AND user_id=?""",
                (rating, metric_id[0],item_id[0], user_id),
            )
            self.cursor.commit()
        except Exception as e:
            print(e)
            return "could not update rating"
        return "rating updated"

    def change_available_date(
        self, guild_id: str, item_name: str, available_to_rate_date: str
    ) -> None:
        try:
            self.cursor.execute(
                "SELECT ri.id FROM ratings.item AS ri INNER JOIN ratings.category AS rc ON ri.category_id = rc.id WHERE rc.guild_id=? AND ri.name=?",
                (guild_id, item_name),
            )
            item_id = self.cursor.fetchone()
            self.cursor.execute(
                "UPDATE ratings.item SET available_to_rate_date=? WHERE id=?",
                (available_to_rate_date, item_id[0]),
            )
            self.cursor.commit()
        except Exception as e:
            print(e)
            return "could not change available date"
        return "available date changed"

    def mark_as_announced(self,item_id):
        try:
            self.cursor.execute(
                "UPDATE ratings.item SET announced=1 WHERE id=?",
                (item_id),
            )
            self.cursor.commit()
        except Exception as e:
            print(e)
            return "could not mark as announced"
        return "marked as announced"

    def set_announcement_channel(self, guild_id, channel_id, category_id):
        try:
            self.cursor.execute(
                "UPDATE ratings.category SET announcement_channel_id=? WHERE guild_id=? AND id=?",
                (channel_id, guild_id, category_id),
            )
            self.cursor.commit()
        except Exception as e:
            print(e)
            return "could not set announcement channel"
        return "announcement channel set"
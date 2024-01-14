import pyodbc

#TODO: enable a way to check for multiple databases and set them up dynamically
# maybe YAML? 

def initialize_db():
    master_connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=master;trusted_connection=yes;'
    rate_my_connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=rate_my;trusted_connection=yes;'
    rate_my_db_check = "SELECT * FROM sys.databases WHERE name = 'rate_my';"
    create_database = "CREATE DATABASE rate_my;"
    
    categories_table = """
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'categories')
    CREATE TABLE [categories] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [guild_id] VARCHAR(20) NOT NULL,
        [category_name] VARCHAR(255) NOT NULL,
        [category_description] VARCHAR(4000) NULL,
        [created_at] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );"""
    item_to_rate_table = """
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'items_to_rate')
    CREATE TABLE [items_to_rate] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [guild_id] VARCHAR(20) NOT NULL,
        [category_id] INT NOT NULL,
        [name] VARCHAR(255) NOT NULL,
        [description] VARCHAR(4000) NULL,
        [available_to_rate_date] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        [created_at] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );"""
    ratings_table = """
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ratings')
    CREATE TABLE [ratings] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [guild_id] VARCHAR(20) NOT NULL,
        [item_id] INT NOT NULL,
        [user_id] VARCHAR(20) NOT NULL,
        [rating] INT NOT NULL,
        [created_at] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );""" 
    master = pyodbc.connect(master_connection_string,autocommit=True)
    master_cursor = master.cursor()
    is_db = master_cursor.execute(rate_my_db_check).fetchone()
    if is_db is None:
        master_cursor.execute(create_database)
    rate_my = pyodbc.connect(rate_my_connection_string)
    with rate_my.cursor() as cursor:
        cursor.execute(categories_table)
        cursor.execute(item_to_rate_table)
        cursor.execute(ratings_table)
        rate_my.commit()
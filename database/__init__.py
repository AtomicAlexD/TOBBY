import pyodbc

class DatabaseCreator:
    def __init__(self, db_config_file):
        self.db_config = db_config_file

    def create_database(self):
        
        # Connect to the master database
        master_connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=master;trusted_connection=yes;'
        master_conn = pyodbc.connect(master_connection_string,autocommit=True)
        master_cursor = master_conn.cursor()

        # Check if the database exists
        db_name = self.db_config['database_name']
        db_check_query = f"SELECT * FROM sys.databases WHERE name = '{db_name}';"
        is_db_exists = master_cursor.execute(db_check_query).fetchone()

        # Create the database if it doesn't exist
        if is_db_exists is None:
            create_db_query = f"CREATE DATABASE {db_name};"
            master_cursor.execute(create_db_query)
        master_conn.close()

        # Connect to the created database
        db_connection_string = f"Driver={{ODBC Driver 17 for SQL Server}};Server=localhost;Database={db_name};trusted_connection=yes;"
        db_conn = pyodbc.connect(db_connection_string)
        db_cursor = db_conn.cursor()

        # Create schemas and tables
        for schema_dict in self.db_config['schema']:
            schema = schema_dict['name']
            create_schema_query = f"IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema}')\n" \
                                  f"EXEC('CREATE SCHEMA {schema};')"
            db_cursor.execute(create_schema_query)

            for table_dict in schema_dict['tables']:
                table = table_dict['name']
                columns = []

                for column in table_dict['columns']:
                    column_string = f"[{column['name']}] {column['type']}"
                    if column.get('primary_key', False):
                        column_string += ' IDENTITY(1,1) PRIMARY KEY'
                    if not column.get('nullable', True):
                        column_string += ' NOT NULL'
                    if column.get('default', False):
                        column_string += f" DEFAULT {column['default']}"
                    #if column.get('foreign_key', False):
                    #    column_string += f" FOREIGN KEY REFERENCES {column['references']}"
                    columns.append(column_string)

                create_table_query = f"IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{table}' AND schema_id = SCHEMA_ID('{schema}'))\n" \
                                     f"EXEC('CREATE TABLE {schema}.[{table}] ({', '.join(columns)})')"
                db_cursor.execute(create_table_query)

        db_conn.commit()
        db_conn.close()

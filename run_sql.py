import pyodbc
import pandas as pd

server = 'chatbotserver456.database.windows.net'
database = 'chatdb'
username = 'sqlserver'
password = 'chatbot@123'
driver = '{ODBC Driver 18 for SQL Server}'  # Update the driver as necessary
# Connection string
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def execute_query_cursor(sql_in):
# Database connection parameters

  
    #print(conn_str)
    try:
        # Establishing the connection to the database
        with pyodbc.connect(conn_str) as conn:
           
            # Create a new cursor
            cursor = conn.cursor()
         
            # Execute the query
            cursor.execute(sql_in)
         
            # Fetch all rows from the query result
            rows = cursor.fetchall()
         
            # Process the rows (example: print them)
            for row in rows:
                print(row)

    except Exception as e:
        print(f"An error occurred: {e}")
        
    return rows


def execute_query_df(sql_in):
    with pyodbc.connect(conn_str) as conn:
        df =pd.read_sql(sql_in, conn)
        print(f'Dataframe \n\n {df}')
    return df

    

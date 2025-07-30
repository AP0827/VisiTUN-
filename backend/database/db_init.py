import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from config import DB_CONFIG

#create a cursor object
        # creates a connection to the database. the ** means that it unpacks the dictionary from DB_CONFIG
conn = psycopg2.connect(**DB_CONFIG)

def init_db():
    try:
        cursor = conn.cursor()
        with open("database/schema.sql", "r") as f:
            #executes every line from the schema creating our database.
            cursor.execute(f.read())
        
        #commits the changes
        conn.commit()
        print("PostgreSQL database initialized")
    except Exception as e:
        print(f"Unexpected Error has occured : {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
import psycopg2
from config import DB_CONFIG
import hashlib
import os

class UserModel:

    def __init__(self):
        self.db_config = DB_CONFIG

    def get_connection(self):
        return psycopg2.connect(**self.db_config)
        

    def create_user(self,username:str,password:str, profile_picture: str = None):
        # Create a new user
        try: 
            conn = self.get_connection()
            cursor = conn.cursor()

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
            query = """
                INSERT INTO Users (username, password, profile_picture)
                VALUES (%s,%s,%s)
                RETURNING user_id
            """

            cursor.execute(query,(username,hashed_password,profile_picture))
            user_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            conn.close()

            return user_id
        except psycopg2.IntegrityError:
            print("Username already exists")
            if conn:
                conn.rollback()
                conn.close()  
            return None  

    def authenticate_user(self,username:str, password:str):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            hashed_password = hashlib.sha256(password.encode).hexdigest()

            query = """
                SELECT user_id, username, profile_picture
                FROM Users 
                WHERE username = %s AND password = %s
            """

            cursor.execute(query,(username,hashed_password))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user:
                return{
                    'user_id' : user[0],
                    'username' : user[1],
                    'profile_picture' : user[2]
                }

            return None
        except Exception as e:
            print(f"Error authenticating user : {e}")
            if conn:
                conn.close()
            return None
    
    def get_user_by_id(self, user_id : int):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT user_id, username, profile_picture FROM User
                WHERE user_id = %s
            """

            cursor.execute(query,{user_id,})
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user:
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'profile_picture': user[2]
                }
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            if conn:
                conn.close()
            return None

            
    


    
import psycopg2
from datetime import datetime
from config import DB_CONFIG

class MessageModel:
    def __init__(self):
        self.db_config = DB_CONFIG
    
    def get_connection(self):
        # ** : dictionary unpacking operator
        return psycopg2.connect(**self.db_config)
    
    def create_message(self, sender_id : int, receiver_id : int, encrypted_message : str, nonce : str, tag : str):
        try : 
            conn = self.get_connection()
            cursor = conn.cursor()
            time = datetime.now()

            query = """
                INSERT INTO Messages 
                (sender_id, receiver_id, message_text, nonce, tag, sent_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING message_id
            """
            
            cursor.execute(query, (sender_id, receiver_id, encrypted_message, nonce, tag, time))
            message_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            conn.close()

            if message_id : 
                return message_id
            
        except psycopg2.IntegrityError as e:
            print("Message already exists.")
            if conn : 
                conn.rollback()
                conn.close()
    
    def get_messages_between_users(self, user1_id : int, user2_id : int, limit : 50):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT message_id, sender_id, receiver_id, message_text, nonce, tag, sent_at FROM Messages
                WHERE 
                (sender_id = %s AND receiver_id = %s)
                OR
                (sender_id = %s AND receiver_id = %s)
                ORDER BY sent_at DESC
                LIMIT %s
            """
            
            cursor.execute(query,(user1_id,user2_id,user2_id,user1_id,limit))
            message = cursor.fetchall()

            cursor.close()
            conn.close()

            if message :
                return [
                    {
                        'message_id' : msg[0],
                        'sender_id' : msg[1],
                        'receiver_id' : msg[2],
                        'message_text' : msg[3],
                        'nonce' : msg[4],
                        'tag' : msg[5],
                        'sent_at' : msg[6]
                    }
                    for msg in message
                ]
            return None
        except Exception as e:
            print(f"Error Fetching user : {e}")
            if conn:
                conn.close()
            return None
    
    def clear_messages_between_users(self , user1_id : int, user2_id : int):
        try : 
            conn = self.get_connection()
            cursor = conn.cursor()
    
            query = """
                DELETE FROM Messages
                WHERE 
                (sender_id = %s AND receiver_id = %s)
                OR
                (sender_id = %s AND receiver_id = %s)
            """
    
            cursor.execute(query,(user1_id,user2_id,user2_id,user1_id))
            conn.commit()
    
            return True
        except Exception as e:
            print(f"Error clearing messages: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    



            



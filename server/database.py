import mysql.connector 
from config import DB_CONFIG

class FAAdb:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(DB_CONFIG)
            if self.conn.is_connected():
                print("success connect...")
        except Exception as e:
            print("failed connect...", e)

    def commit(self):
        self.conn.commit()
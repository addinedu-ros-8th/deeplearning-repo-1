import mysql.connector 

import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DB_CONFIG

class FAAdb:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            if self.conn.is_connected():
                print("success connect...")
        except Exception as e:
            print("failed connect...", e)

    def commit(self):
        self.conn.commit()
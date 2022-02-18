import mysql.connector
import json

class UseDatabase:
    def __init__(self,config:dict):
        self.configuration = config

    def __enter__(self):
        self.connection = mysql.connector.connect(**self.configuration)
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self,a,b,c):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

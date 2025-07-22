# pip install mysql-connector-python - in the command line


import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host = 'ich-edit.edu.itcareerhub.de',
            username = 'ich1',
            password = 'ich1_password_ilovedbs',
            database = '170624_Kazakevych'
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
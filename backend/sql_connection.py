import mysql.connector

# global variable
__conn = None
def get_sql_connection():
    global __conn
    
    if __conn is None:
        # connect to the database
        __conn = mysql.connector.connect(user='root', password='root',
                                    host='127.0.0.1',
                                    database='grocery_store')
    return __conn
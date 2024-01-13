
import psycopg2

class Database:
    def __init__(self, host, port, db_name, user, password):
        self.host = host
        self.port = port
        self.name = db_name
        self.user = user
        self.password = password




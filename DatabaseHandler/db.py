import psycopg2
import re


class Database:
    def __init__(self, host, port, db_name, user, password):
        self._host = host
        self._port = port
        self._name = db_name
        self._user = user
        self._password = password

    def __get_conn_cur(self):
        try:
            conn = psycopg2.connect(host=self._host, port=self._port, user=self._user, password=self._password,
                                    database=self._name)
            cursor = conn.cursor()
            return conn, cursor
        except:
            return None

    def __close_conn_cur(self, conn, cur):
        try:
            conn.close()
            cur.close()
            return True
        except:
            return False

    def check_connection(self):
        try:
            conn, cur = self.__get_conn_cur()
            cur.execute("SELECT version();")
            result = cur.fetchone()
            if result:
                return True
        except:
            return False

    def select(self, table, columns=None, filters=None):
        conn, cur = self.__get_conn_cur()
        if columns:
            cols = ', '.join([f'{c}' for c in columns])
            command = f"""SELECT {cols} FROM {table};"""
        else:
            command = f"""SELECT * FROM {table};"""

        if filters:
            command = command[:-1] + f"""WHERE {filters};"""

        try:
            cur.execute(command)
            result = cur.fetchall()
            self.__close_conn_cur(conn, cur)
            return result
        except:
            return None

    def exact_exec(self, command, force=False):
        conn, cur = self.__get_conn_cur()
        if force:
            cur.execute(command)
            result = cur.fetchall()
        else:
            try:
                cur.execute(command)
                result = cur.fetchall()
            except:
                result = None

        self.__close_conn_cur(conn, cur)
        return result

    def insert(self, table, columns, data):
        conn, cur = self.__get_conn_cur()
        data = ',\n'.join(str(d) for d in data)
        if columns:
            cols = ', '.join(columns)
            command = f"""INSERT INTO {table} ({cols}) VALUES {data};"""
        else:
            command = f"""INSERT INTO {table} VALUES {data};"""
        try:
            cur.execute(command)
            conn.commit()
            result = True
        except:
            result = None

        self.__close_conn_cur(conn, cur)
        return result




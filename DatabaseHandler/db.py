import psycopg


class Database:
    def __init__(self, host, port, db_name, user, password):
        self._host = host
        self._port = port
        self._name = db_name
        self._user = user
        self._password = password

    def __get_conn_cur(self):
        try:
            conn = psycopg.connect(host=self._host, port=self._port, user=self._user, password=self._password,
                                   dbname=self._name)
            cursor = conn.cursor()
            return conn, cursor
        except Exception as e:
            print(type(e), e)
            return None, None

    def __close_conn_cur(self, conn, cur):
        try:
            conn.close()
            cur.close()
            return True
        except Exception as e:
            return False

    def check_connection(self):
        try:
            conn, cur = self.__get_conn_cur()
            cur.execute("SELECT version();")
            result = cur.fetchone()
            if result:
                return True, result
        except:
            return False

    def create_database(self, name):
        conn, cur = self.__get_conn_cur()
        conn.autocommit = True
        command = f"CREATE DATABASE {name};"
        try:
            cur.execute(command)
            result = True, command
        except Exception as e:
            result = False, command, e
        self.__close_conn_cur(conn, cur)
        return result

    def create_table(self, table_name, fields):
        conn, cur = self.__get_conn_cur()
        flds = ',\n'.join([f"{col} {dtype}" for col, dtype in fields.items()])
        command = f"""CREATE TABLE {table_name} ({flds});"""
        try:
            cur.execute(command)
            conn.commit()
            result = True, command
        except Exception as e:
            result = False, command, e

        self.__close_conn_cur(conn, cur)
        return result

    def drop_table(self, table_name):
        conn, cur = self.__get_conn_cur()
        command = f"""DROP TABLE {table_name};"""
        try:
            cur.execute(command)
            conn.commit()
            result = True, command
        except Exception as e:
            result = False, command, e

        self.__close_conn_cur(conn, cur)
        return result

    def select(self, table, columns=None, filters=None, filter_values=None, Model=None):
        conn, cur = self.__get_conn_cur()
        if columns:
            cols = ', '.join([f'{c}' for c in columns])
            command = f"""SELECT {cols} FROM {table};"""
        else:
            command = f"""SELECT * FROM {table};"""

        if filters:
            command = command[:-1] + f""" WHERE {filters};"""

        try:
            # print(command)
            if filter_values:
                cur.execute(command, filter_values)
            else:
                cur.execute(command)
            if Model:
                objects = []
                records = cur.fetchall()
                for record in records:
                    objects.append(Model(*record))
                result = objects, command
            else:
                result = cur.fetchall(), command

        except Exception as e:
            result = None, command, e

        self.__close_conn_cur(conn, cur)
        return result

    def exact_exec(self, command, values=None, fetch=False):
        conn, cur = self.__get_conn_cur()
        try:
            if values:
                cur.execute(command, values)
            else:
                cur.execute(command)
            result = True, command
            if fetch:
                result = True, cur.fetchall(), command
            conn.commit()
        except Exception as e:
            result = None, command, e

        self.__close_conn_cur(conn, cur)
        return result

    def insert(self, table, columns, data):
        conn, cur = self.__get_conn_cur()
        place_holders = ('%s, '*len(data))[:-2]
        if columns:
            cols = ', '.join(columns)
            command = f"""INSERT INTO {table} ({cols}) VALUES ({place_holders});"""
        else:
            command = f"""INSERT INTO {table} VALUES ({place_holders});"""
        try:
            cur.execute(command, data)
            conn.commit()
            result = True, command
        except Exception as e:
            result = None, command, e

        self.__close_conn_cur(conn, cur)
        return result

    def delete(self, table, filters):
        conn, cur = self.__get_conn_cur()
        command = f"""DELETE FROM {table} WHERE {filters};"""
        try:
            cur.execute(command)
            conn.commit()
            result = True, command
        except Exception as e:
            result = False, command, e

        self.__close_conn_cur(conn, cur)
        return result

    def update(self, table, updates, filters=None):
        conn, cur = self.__get_conn_cur()
        upds = ', '.join([f"{k}='{v}'" for k, v in updates.items()])
        command = f"""UPDATE {table} SET {upds} WHERE {filters};"""
        try:
            cur.execute(command)
            conn.commit()
            result = True, command
        except Exception as e:
            result = False, command, e

        self.__close_conn_cur(conn, cur)
        return result

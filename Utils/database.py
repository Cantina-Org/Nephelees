import mariadb


class DataBase:
    def __init__(self, user, password, host, port, database):
        self.database = database
        self.port = port
        self.host = host
        self.password = password
        self.user = user
        self.cursor = None
        self.connector = None

    def connection(self):
        self.connector = mariadb.connect(user=self.user, password=self.password, host=self.host, port=self.port,
                                         database=self.database)
        self.cursor = self.connector.cursor()

    def create_table(self, body):
        self.cursor.execute(body)
        self.connector.commit()

    def insert(self, body, args):
        retry = True
        while retry:
            try:
                if args:
                    self.cursor.execute(body, args)
                    self.connector.commit()
                else:
                    return "Error: Args Is Needed"
                retry = False
                return True
            except mariadb.InterfaceError:
                self.cursor.close()
                self.connector.close()
                self.connection()
                retry = True

    def select(self, body, args=None, number_of_data=None):
        data = None
        retry = True
        while retry:
            try:
                if args:
                    self.cursor.execute(body, args)
                else:
                    self.cursor.execute(body)
                if not number_of_data:
                    data = self.cursor.fetchall()
                elif number_of_data == 1:
                    data = self.cursor.fetchone()
                else:
                    data = self.cursor.fetchmany(number_of_data)
                retry = False
                return data
            except mariadb.InterfaceError:
                self.cursor.close()
                self.connector.close()
                self.connection()
                retry = True

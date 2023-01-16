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
        pass

    def select(self, body, args, number_of_data):
        retry = True
        while retry:
            try:
                self.cursor.execute(body, args)
                if number_of_data == 0:
                    data = self.cursor.fetchall()
                else:
                    data = self.cursor.fetchmany(number_of_data)
                retry = False
                return data
            except mariadb.InterfaceError:
                self.cursor.close()
                self.connector.close()
                self.connection()
                retry = True

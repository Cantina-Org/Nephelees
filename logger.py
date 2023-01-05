import mariadb

con = mariadb.connect(user="mathieu", password="LeMdPDeTest", host="localhost", port=3306, database="cantina_db")
cursor = con.cursor()

class logger:
    def __int__(self):
        pass

    def log_l1(self, user_name, user_action):
        pass
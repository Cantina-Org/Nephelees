import mariadb
import os
import json

conf_file = os.open(os.path.abspath(os.getcwd()) + "/config.json", os.O_RDONLY)
config_data = json.loads(os.read(conf_file, 150))

con = mariadb.connect(user=config_data['database_username'], password=config_data['database_password'],
                      host="localhost", port=3306, database=config_data['database_name'])
cursor = con.cursor()


def f_user_name(user_id):
    cursor.execute("""SELECT user_name FROM user WHERE token=?""", (user_id,))
    data = cursor.fetchone()
    print(data[0])
    return data[0]

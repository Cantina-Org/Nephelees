from os import *
from flask import Flask, render_template, request
import mariadb

con = mariadb.connect(user="mathieu", password="LeMdPDeTest", host="localhost", port=3306, database="cantina_db")
cursor = con.cursor()
# cursor.execute("CREATE TABLE instance(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, "
#               "nom_instance TEXT, ip TEXT, official BOOL, private BOOL, usefull_data BOOL, owner_id INT, "
#               "moderator_id TEXT, user_id TEXT, online BOOL, last_online TEXT, warn_level INT)")

con.commit()

dir_path = "/home/mathieu/Bureau/cantina/file_cloud"
app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('home.html')


@app.route('/my/file/')
def show_file():
    args = request.args
    file = []
    dir = []
    for (dirpath, dirnames, filenames) in walk(dir_path + args.get('path')):
        file.extend(filenames)
        dir.extend(dirnames)
        break

    if args.get('path') != "/":
        path2 = args.get('path') + "/"
    elif args.get('path') == "/":
        path2 = args.get('path')

    return render_template('myfile.html', dir=dir, file=file, path=path2)


if __name__ == '__main__':
    app.run()

import os
from os import *
from flask import Flask, render_template, request, url_for
import mariadb

con = mariadb.connect(user="mathieu", password="LeMdPDeTest", host="localhost", port=3306, database="cantina_db")
cursor = con.cursor()
# cursor.execute("CREATE TABLE instance(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, "
#               "nom_instance TEXT, ip TEXT, official BOOL, private BOOL, usefull_data BOOL, owner_id INT, "
#               "moderator_id TEXT, user_id TEXT, online BOOL, last_online TEXT, warn_level INT)")

con.commit()

path2, filenames = "", ""
dir_path = "/home/mathieu/Bureau/cantina/file_cloud"
app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('home.html')


@app.route('/my/file/')
def file():
    global path2, filenames
    args = request.args
    work_file_in_dir, work_dir = [], []

    if not args.getlist('path'):
        for (dirpath, dirnames, filenames) in walk(dir_path):
            work_file_in_dir.extend(filenames)
            work_dir.extend(dirnames)
            break
    else:
        for (dirpath, dirnames, filenames) in walk(dir_path + args.get('path')):
            work_file_in_dir.extend(filenames)
            work_dir.extend(dirnames)
            break

    if not args.get('path'):
        path2 = "/"
    elif args.get('path') != "/":
        path2 = args.get('path') + "/"
    elif args.get('path') == "/":
        path2 = args.get('path')

    if not args.get('action') or args.get('action') == 'show':
        return render_template('myfile.html', dir=work_dir, file=work_file_in_dir, path=path2)
    elif args.get('action') == "delete" and args.get('workFile') and args.get('workFile') in filenames:
        os.remove(dir_path+path2+args.get('workFile'))
        return render_template("redirect/r-myfile.html", path="/my/file/?path=/")
    elif args.get('action') == "create" and args.get('workFile'):
        fd = os.open(dir_path+path2+args.get('workFile'), os.O_RDWR | os.O_CREAT)
        os.close(fd)
        return render_template("redirect/r-myfile.html", path="/my/file/?path=/")
    else:
        return 'AREUH'



if __name__ == '__main__':
    app.add_url_rule('/favicon.ico',
                     redirect_to=url_for('static', filename='static/favicon.ico'))
    app.run()

import os
from os import *
from flask import Flask, render_template, request, url_for, redirect, make_response
import mariadb

con = mariadb.connect(user="mathieu", password="LeMdPDeTest", host="localhost", port=3306, database="cantina_db")
cursor = con.cursor()
#cursor.execute("CREATE TABLE user(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, "
#           "user_name TEXT, password TEXT, admin BOOL, online BOOL, last_online TEXT)")

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
    userToken = request.cookies.get('userID')
    if userToken != "ee":
        return redirect(url_for('hello_world'))
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

@app.route('/setcookies')
def setCookies():
    resp = make_response(redirect(url_for('hello_world')))
    resp.set_cookie('userID', "ee")

    return resp


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
        passwd = request.form['passwd']

        if cursor.execute(f'SELECT user_name, password FROM user WHERE password = {passwd}'):
            resp = make_response(redirect(url_for('hello_world')))
            resp.set_cookie('userID', user)
            return resp

        else:


    elif request.method == 'GET':
        return render_template('login.html')

if __name__ == '__main__':
    app.add_url_rule('/favicon.ico',
                     redirect_to=url_for('static', filename='static/favicon.ico'))
    app.run()

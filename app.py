from werkzeug.utils import secure_filename
from os import *
from flask import Flask, render_template, request, url_for, redirect, make_response
import mariadb
import hashlib
import os


def hash_perso(passwordtohash):
    passw = passwordtohash.encode()
    passw = hashlib.md5(passw).hexdigest()
    passw = passw.encode()
    passw = hashlib.sha256(passw).hexdigest()
    passw = passw.encode()
    passw = hashlib.sha512(passw).hexdigest()
    passw = passw.encode()
    passw = hashlib.md5(passw).hexdigest()
    return passw

con = mariadb.connect(user="mathieu", password="LeMdPDeTest", host="localhost", port=3306, database="cantina_db")
cursor = con.cursor()
#cursor.execute("CREATE TABLE user(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, "
#           "user_name TEXT, password TEXT, admin BOOL, online BOOL, last_online TEXT)")

# cursor.execute(f"""INSERT INTO user(token, user_name, password, admin) VALUES ('MC8Qt~KApaCT)VX>FBs*y$~:^=ll$^', 'matbe3', '{hash_perso("Asvel2021_._")}', 0)""")

con.commit()

path2, filenames = "", ""
dir_path = "/home/mathieu/Bureau/cantina/file_cloud"
app = Flask(__name__)
app.config['UPLOAD_PATH'] = dir_path

@app.route('/')
def hello_world():  # put application's code here
    return render_template('home.html')


@app.route('/my/file/')
def file():
    global path2, filenames
    userToken = request.cookies.get('userID')
    cursor.execute(f'''SELECT token FROM user WHERE admin''',)
    row = cursor.fetchall()
    if not [tup for tup in row if userToken in tup]:
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
        cursor.execute(f'''SELECT user_name, password, token FROM user WHERE password = ? AND user_name = ?''', (hash_perso(passwd), user))
        row = cursor.fetchone()

        try:
            if len(row) >= 1:
                resp = make_response(redirect(url_for('hello_world')))
                resp.set_cookie('userID', row[2])
                return resp
        except:
            return redirect(url_for("hello_world"))


    elif request.method == 'GET':
        return render_template('login.html')


@app.route('/my/file/upload', methods=['GET', 'POST'])
def upload_file():
    args = request.args
    if request.method == 'GET':
        return render_template('upload_file.html')

    elif request.method == 'POST':
        userToken = request.cookies.get('userID')
        cursor.execute(f'''SELECT token FROM user WHERE admin''', )
        row = cursor.fetchall()
        if not [tup for tup in row if userToken in tup]:
            return redirect(url_for('hello_world'))

        f = request.files['file']
        f.save(os.path.join(dir_path+args.get('path'), secure_filename(f.filename)))
        return 'file uploaded successfully'


if __name__ == '__main__':
    app.add_url_rule('/favicon.ico',
                     redirect_to=url_for('static', filename='static/favicon.ico'))
    app.run()

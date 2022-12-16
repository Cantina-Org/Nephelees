from werkzeug.utils import secure_filename
from os import *
from flask import Flask, render_template, request, url_for, redirect, make_response, send_from_directory
import mariadb
import hashlib
import os
import uuid


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
cursor.execute("CREATE TABLE IF NOT EXISTS user(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, "
           "user_name TEXT, password TEXT, admin BOOL, online BOOL, last_online TEXT)")

# cursor.execute(f"""INSERT INTO user(token, user_name, password, admin) VALUES ({uuid.uuid3(uuid.uuid1(), str(uuid.uuid1()))}, 'matbe3', '{hash_perso("")}', 0)""")

con.commit()

path2, filenames, lastPath = "", "", ""
dir_path = "/home/mathieu/Bureau/cantina/file_cloud"
app = Flask(__name__)
app.config['UPLOAD_PATH'] = dir_path

@app.route('/')
def hello_world():  # put application's code here
    cursor.execute('''SELECT user_name FROM user WHERE token = ?''', (request.cookies.get('userID'),))
    return render_template('home.html', cur=cursor.fetchall())


@app.route('/my/file/')
def file():
    global path2, filenames, lastPath
    userToken = request.cookies.get('userID')
    cursor.execute(f'''SELECT token FROM user WHERE admin''',)
    row = cursor.fetchall()

    if not [tup for tup in row if userToken in tup]:
        return redirect(url_for('hello_world'))

    args = request.args
    lastPath = ""
    work_file_in_dir, work_dir = [], []


    if not args.getlist('path'):
        for (dirpath, dirnames, filenames) in walk(dir_path):
            work_file_in_dir.extend(filenames)
            work_dir.extend(dirnames)
            break

    else:
        last_path_1 = args.get('path')
        last_path_1 = last_path_1[:-1].split("/")
        for i in range(0, len(last_path_1)-1):
            lastPath = lastPath + last_path_1[i]+'/'

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
        return render_template('myfile.html', dir=work_dir, file=work_file_in_dir, path=path2, lastPath=lastPath)

    elif args.get('action') == "deleteFile" and args.get('workFile') and args.get('workFile') in filenames:
        os.remove(dir_path+path2+args.get('workFile'))
        return render_template("redirect/r-myfile.html", path="/my/file/?path=/", lastPath=lastPath)

    elif args.get('action') == "createFile" and args.get('workFile'):
        fd = os.open(dir_path+path2+args.get('workFile'), os.O_RDWR | os.O_CREAT)
        os.close(fd)
        return render_template("redirect/r-myfile.html", path="/my/file/?path=/", lastPath=lastPath)

    elif args.get('action') == "deleteFolder" and args.get('workFile') and args.get('workFile') in filenames:
        os.rmdir(dir_path+path2+args.get('workFile'))
        return render_template("redirect/r-myfile.html", path="/my/file/?path=/", lastPath=lastPath)

    elif args.get('action') == "createFolder" and args.get('workFile'):
        os.mkdir(dir_path+path2+args.get('workFile'))
        return render_template("redirect/r-myfile.html", path="/my/file/?path=/", lastPath=lastPath)

    else:
        return render_template('myfile.html', dir=work_dir, file=work_file_in_dir, path=path2, lastPath=lastPath)


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
        return redirect(url_for('file', path=args.get('path')))


@app.route('/my/file/download')
def download_file():
    args = request.args

    userToken = request.cookies.get('userID')
    cursor.execute(f'''SELECT token FROM user WHERE admin''', )
    row = cursor.fetchall()

    if not [tup for tup in row if userToken in tup]:
        return redirect(url_for('hello_world'))

    return send_from_directory(directory=dir_path+args.get('path'), path=args.get('item'))


if __name__ == '__main__':
    app.add_url_rule('/favicon.ico',
                     redirect_to=url_for('static', filename='static/favicon.ico'))
    app.run()

from werkzeug.utils import secure_filename
from os import *
from flask import Flask, render_template, request, url_for, redirect, make_response, send_from_directory
import mariadb
import hashlib
import os
import subprocess
import uuid
import shutil


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


def user_login():
    cursor.execute('''SELECT user_name, admin FROM user WHERE token = ?''', (request.cookies.get('userID'),))
    data = cursor.fetchall()

    if data[0][0] != '' and data[0][1]:
        return True, True
    elif data[0][0] != '' and not data[0][1]:
        return True, False
    else:
        return False, False


def make_log(action_name, user_ip, user_token, log_level, argument=None):
    cursor.execute('''INSERT INTO log(name, user_ip, user_token, argument, log_level) VALUES (?,?, ?,?,?)''',
                   (str(action_name), str(user_ip), str(user_token), argument, log_level))
    con.commit()


con = mariadb.connect(user="cantina", password="LeMdPDeTest", host="localhost", port=3306, database="cantina_db")
cursor = con.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS user(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, "
               "user_name TEXT, password TEXT, admin BOOL, work_Dir TEXT, online BOOL, last_online TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS log(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, name TEXT, user_ip text,"
               "user_token TEXT, argument TEXT, log_level INT, date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")

con.commit()

fd, filenames, lastPath = "", "", ""
dir_path = os.path.abspath(os.getcwd()) + '/file_cloud/'
app = Flask(__name__)
app.config['UPLOAD_PATH'] = dir_path


@app.route('/')
def home():  # put application's code here
    cursor.execute('''SELECT user_name, admin FROM user WHERE token = ?''', (request.cookies.get('userID'),))
    return render_template('home.html', cur=cursor.fetchall())


@app.route('/my/file/')
def file():
    global filenames, lastPath, fd
    actual_path, lastPath = '/', '/'
    args = request.args
    work_file_in_dir, work_dir = [], []
    user_token = request.cookies.get('userID')

    cursor.execute(f'''SELECT work_Dir, admin FROM user WHERE token = ?''', (user_token,))
    row = cursor.fetchone()

    if not args.getlist('path'):
        if row[1]:
            for (dirpath, dirnames, filenames) in walk(dir_path):
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break
        elif not row[1]:
            for (dirpath, dirnames, filenames) in walk(row[0]):
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break

    else:
        actual_path_not_corrected = args.get('path').split("/")
        for i in actual_path_not_corrected:
            if i:
                actual_path += i + '/'

        last_path_1 = actual_path[:-1].split("/")
        for i in range(0, len(last_path_1) - 1):
            if last_path_1[i]:
                lastPath = lastPath + last_path_1[i] + '/'

        if row[1]:
            for (dirpath, dirnames, filenames) in walk(dir_path + '/' + args.get('path')):
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break
            print(dir_path + args.get('path'))
        elif not row[1]:
            for (dirpath, dirnames, filenames) in walk(row[0] + args.get('path')):
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break

    if not args.get('action') or args.get('action') == 'show':
        return render_template('myfile.html', dir=work_dir, file=work_file_in_dir, path=actual_path,
                               lastPath=lastPath)

    elif args.get('action') == "deleteFile" and args.get('workFile') and args.get('workFile') in filenames:
        if row[1]:
            os.remove(dir_path + actual_path + args.get('workFile'))
        elif not row[1]:
            os.remove(row[0] + '/' + actual_path + args.get('workFile'))
        return render_template("redirect/r-myfile.html", path="/my/file/?path=/"+actual_path, lastPath=lastPath)

    elif args.get('action') == "createFile" and args.get('workFile'):
        if row[1]:
            fd = os.open(dir_path + args.get('path') + "/" + args.get('workFile'), os.O_RDWR | os.O_CREAT)
        elif not row[1]:
            fd = os.open(row[0] + '/' + args.get('path') + "/" + args.get('workFile'), os.O_RDWR | os.O_CREAT)
        os.close(fd)
        print('path: '+args.get('path'))
        return render_template("redirect/r-myfile.html", path="/my/file/?path=/"+actual_path, lastPath=lastPath)

    elif args.get('action') == "deleteFolder" and args.get('workFile') and args.get('workFile') in work_dir:
        if row[1]:
            shutil.rmtree(dir_path + actual_path + "/" + args.get('workFile'))
        elif not row[0]:
            shutil.rmtree(row[0] + '/' + actual_path + args.get('workFile'))
        print(lastPath)
        print(actual_path)
        return render_template("redirect/r-myfile.html", path="/my/file/?path=/"+actual_path)

    elif args.get('action') == "createFolder" and args.get('workFile'):
        if row[1]:
            os.mkdir(dir_path + actual_path + args.get('workFile'))
        elif not row[1]:
            os.mkdir(row[0] + '/' + actual_path + args.get('workFile'))
        return render_template("redirect/r-myfile.html", path="/my/file/?path=/"+args.get('path'), lastPath=lastPath)

    else:
        return render_template('myfile.html', dir=work_dir, file=work_file_in_dir, path=args.get('path') + "/",
                               lastPath=lastPath)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
        passwd = request.form['passwd']
        cursor.execute(f'''SELECT user_name, password, token FROM user WHERE password = ? AND user_name = ?''',
                       (hash_perso(passwd), user))
        row = cursor.fetchone()

        try:
            if len(row) >= 1:
                make_log('login', request.remote_addr, row[2], 1)
                resp = make_response(redirect(url_for('home')))
                resp.set_cookie('userID', row[2])
                return resp
        except Exception as e:
            print(e)
            return redirect(url_for("home"))

    elif request.method == 'GET':
        return render_template('login.html')


@app.route('/my/file/upload', methods=['GET', 'POST'])
def upload_file():
    args = request.args

    if request.method == 'GET':
        return render_template('upload_file.html')

    elif request.method == 'POST':
        user_token = request.cookies.get('userID')
        cursor.execute(f'''SELECT token FROM user WHERE admin''', )
        row = cursor.fetchall()

        if not [tup for tup in row if user_token in tup]:
            return redirect(url_for('home'))

        f = request.files['file']
        f.save(os.path.join(dir_path + args.get('path'), secure_filename(f.filename)))
        make_log('upload_file', request.remote_addr, request.cookies.get('userID'), 1,
                 os.path.join(dir_path + args.get('path'), secure_filename(f.filename)))
        return redirect(url_for('file', path=args.get('path')))


@app.route('/my/file/download')
def download_file():
    args = request.args

    user_token = request.cookies.get('userID')
    cursor.execute(f'''SELECT token FROM user WHERE admin''')
    row = cursor.fetchall()

    if not [tup for tup in row if user_token in tup]:
        return redirect(url_for('home'))

    make_log('Download file', request.remote_addr, request.cookies.get('userID'), 1,
             dir_path + args.get('path') + args.get('item'))
    return send_from_directory(directory=dir_path + args.get('path'), path=args.get('item'))


@app.route('/admin/home')
def admin_home():
    try:
        count = 0
        admin_and_login = user_login()
        if admin_and_login[0] and admin_and_login[1]:
            for root_dir, cur_dir, files in os.walk(dir_path):
                count += len(files)
            main_folder_size = subprocess.check_output(['du', '-sh', dir_path]).split()[0].decode('utf-8')
            cursor.execute('''SELECT user_name FROM user WHERE token=?''', (request.cookies.get('userID'),))
            user_name = cursor.fetchall()
            return render_template('admin/home.html', data=user_name, file_number=count,
                                   main_folder_size=main_folder_size)
        else:
            return redirect(url_for('home'))

    except Exception as e:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2, str(e))
        return redirect(url_for('home'))


@app.route('/admin/usermanager/')
@app.route('/admin/usermanager/<user_name>')
def admin_user_manager(user_name=None):
    try:
        admin_and_login = user_login()
        if admin_and_login[0] and admin_and_login[1]:
            if user_name:
                cursor.execute('''SELECT * FROM user WHERE user_name=?''', (user_name,))
                user_account = cursor.fetchall()
                return render_template('admin/specific_user_manager.html', user_account=user_account[0])
            else:
                cursor.execute('''SELECT * FROM user''')
                all_account = cursor.fetchall()
                cursor.execute('''SELECT user_name FROM user WHERE token=?''', (request.cookies.get('userID'),))
                user_name = cursor.fetchall()
                return render_template('admin/user_manager.html', user_name=user_name,
                                       all_account=all_account)
        else:
            return redirect(url_for('home'))
    except Exception as e:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2, str(e))
        return redirect(url_for('home'))


@app.route('/admin/add_user/', methods=['POST', 'GET'])
def admin_add_user():
    try:
        admin_and_login = user_login()
        if admin_and_login[0] and admin_and_login[1]:
            if request.method == 'GET':
                cursor.execute('''SELECT user_name FROM user WHERE token=?''', (request.cookies.get('userID'),))
                user_name = cursor.fetchall()
                return render_template('admin/add_user.html', user_name=user_name)
            elif request.method == 'POST':
                if request.form['pword1'] == request.form['pword2']:
                    try:
                        if request.form['admin'] == 'on':
                            admin = True
                        else:
                            admin = False
                    except Exception as e:
                        print(e)
                        admin = False
                    newUUID = str(uuid.uuid3(uuid.uuid1(), str(uuid.uuid1())))
                    cursor.execute('''INSERT INTO user(token, user_name, password, admin, work_Dir) VALUES (?, ?, ?, 
                            ?, ?)''', (newUUID, request.form['uname'], hash_perso(request.form['pword2']), admin,
                                       dir_path + '/' + secure_filename(request.form['uname'])))
                    con.commit()
                    os.mkdir(dir_path + '/' + secure_filename(request.form['uname']))
                    make_log('add_user', request.remote_addr, request.cookies.get('userID'), 2,
                             'Created user token: ' + newUUID)
                    return redirect(url_for('admin_user_manager'))
        else:
            return redirect(url_for('home'))
    except Exception as e:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2, str(e))
        return redirect(url_for('home'))


@app.route('/admin/show_log/')
@app.route('/admin/show_log/<log_id>')
def admin_show_log(log_id=None):
    try:
        admin_and_login = user_login()
        if admin_and_login[0] and admin_and_login[1]:
            if log_id:
                cursor.execute('''SELECT * FROM log WHERE ID=?''', (log_id,))
                log = cursor.fetchone()
                return render_template('admin/specific_log.html', log=log)
            else:
                cursor.execute('''SELECT * FROM log''')
                all_log = cursor.fetchall()
                cursor.execute('''SELECT user_name FROM user WHERE token=?''', (request.cookies.get('userID'),))
                user_name = cursor.fetchall()
                return render_template('admin/show_log.html', user_name=user_name,
                                       all_log=all_log)
    except Exception as e:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2, str(e))
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='static/favicon.ico'))
    app.run()

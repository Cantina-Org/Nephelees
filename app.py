from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, url_for, redirect, make_response, send_from_directory, jsonify
import os
import mariadb
import hashlib
import subprocess
import uuid
import shutil
import random
import string
import tarfile
import json


def hash_perso(passwordtohash):
    try:
        passw = passwordtohash.encode()
    except AttributeError:
        return None
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
    try:
        if data[0][0] != '' and data[0][1]:
            return True, True
        elif data[0][0] != '' and not data[0][1]:
            return True, False
        else:
            return False, False
    except IndexError as e:
        print(e)
        return 'UserNotFound'


def make_log(action_name, user_ip, user_token, log_level, argument=None, content=None):
    if content:
        cursor.execute('''INSERT INTO log(name, user_ip, user_token, argument, log_level) VALUES (?,?, ?,?,?)''',
                       (str(action_name), str(user_ip), str(content), argument, log_level))
    else:
        cursor.execute('''INSERT INTO log(name, user_ip, user_token, argument, log_level) VALUES (?,?, ?,?,?)''',
                       (str(action_name), str(user_ip), str(user_token), argument, log_level))
    con.commit()


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


fd, filenames, lastPath = "", "", ""
dir_path = os.path.abspath(os.getcwd()) + '/file_cloud/'
share_path = os.path.abspath(os.getcwd()) + '/share/'
app = Flask(__name__)
app.config['UPLOAD_PATH'] = dir_path
api_no_token = 'You must send a token in JSON with the name: `api-token`!'
conf_file = os.open(os.path.abspath(os.getcwd()) + "/config.json", os.O_RDONLY)
config_data = json.loads(os.read(conf_file, 150))

con = mariadb.connect(user=config_data['database_username'], password=config_data['database_password'],
                      host="localhost", port=3306, database=config_data['database_name'])
cursor = con.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS user(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, "
               "user_name TEXT, password TEXT, admin BOOL, work_Dir TEXT, online BOOL, last_online TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS log(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, name TEXT, user_ip text,"
               "user_token TEXT, argument TEXT, log_level INT, date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
cursor.execute("CREATE TABLE IF NOT EXISTS file_sharing(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, file_name TEXT, "
               "file_owner text, file_short_name TEXT, login_to_show BOOL DEFAULT 1, password TEXT,"
               "date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
cursor.execute("CREATE TABLE IF NOT EXISTS api(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, api_name TEXT,"
               "api_desc TEXT, owner TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS api_permission(token_api TEXT, create_file BOOL, upload_file BOOL, "
               "delete_file BOOL, create_folder BOOL, delete_folder BOOL, share_file_and_folder BOOL, "
               "delete_share_file_and_folder BOOL, create_user BOOL, delete_user BOOL)")
con.commit()


@app.route('/')
def home():  # put application's code here
    if not request.cookies.get('userID'):
        return redirect(url_for('login'))
    cursor.execute('''SELECT user_name, admin FROM user WHERE token = ?''', (request.cookies.get('userID'),))
    data = cursor.fetchone()
    if data[1]:
        return render_template('home-admin-view.html', cur=cursor.fetchone())
    else:
        return render_template('home.html', cur=cursor.fetchone())


@app.route('/my/file/')
def file():
    global filenames, lastPath, fd
    actual_path, lastPath, rand_name = '/', '/', ''
    args = request.args
    work_file_in_dir, work_dir = [], []
    user_token = request.cookies.get('userID')
    if not user_token:
        return redirect(url_for('login'))

    for i in random.choices(string.ascii_lowercase, k=10):
        rand_name += i

    cursor.execute(f'''SELECT work_Dir, admin, user_name FROM user WHERE token = ?''', (user_token,))
    row = cursor.fetchone()

    if not args.getlist('path'):

        if row[1]:
            for (dirpath, dirnames, filenames) in os.walk(dir_path):
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break
        elif not row[1]:
            for (dirpath, dirnames, filenames) in os.walk(row[0]):
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
            for (dirpath, dirnames, filenames) in os.walk(dir_path + '/' + args.get('path')):
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break
        elif not row[1]:
            for (dirpath, dirnames, filenames) in os.walk(row[0] + args.get('path')):
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
        return render_template("redirect/r-myfile.html", path="/my/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "createFile" and args.get('workFile'):
        if row[1]:
            fd = os.open(dir_path + args.get('path') + "/" + args.get('workFile'), os.O_RDWR | os.O_CREAT)
        elif not row[1]:
            fd = os.open(row[0] + '/' + args.get('path') + "/" + args.get('workFile'), os.O_RDWR | os.O_CREAT)
        os.close(fd)
        return render_template("redirect/r-myfile.html", path="/my/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "deleteFolder" and args.get('workFile') and args.get('workFile') in work_dir:
        if row[1]:
            shutil.rmtree(dir_path + actual_path + "/" + args.get('workFile'))
        elif not row[1]:
            shutil.rmtree(row[0] + '/' + actual_path + args.get('workFile'))

        return render_template("redirect/r-myfile.html", path="/my/file/?path=" + actual_path)

    elif args.get('action') == "createFolder" and args.get('workFile'):
        if row[1]:
            os.mkdir(dir_path + actual_path + args.get('workFile'))
        elif not row[1]:
            os.mkdir(row[0] + '/' + actual_path + args.get('workFile'))
        return render_template("redirect/r-myfile.html", path="/my/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "shareFile" and args.get('workFile') and args.get('loginToShow'):
        if row[1]:
            shutil.copy2(dir_path + actual_path + args.get('workFile'),
                         share_path + row[2] + '/' + args.get('workFile'))
        elif not row[1]:
            shutil.copy2(row[0] + '/' + actual_path + args.get('workFile'),
                         share_path + row[2] + '/' + args.get('workFile'))
        cursor.execute('''INSERT INTO file_sharing(file_name, file_owner, file_short_name, login_to_show, password) 
                                    VALUES (?, ?, ?, ?, ?)''', (args.get('workFile'), row[2],
                                                                rand_name, args.get('loginToShow'),
                                                                hash_perso(args.get('password'))))
        con.commit()
        return render_template("redirect/r-myfile-clipboardcopy.html", short_name=rand_name,
                               path="/my/file/?path=" + actual_path)

    elif args.get('action') == "shareFolder" and args.get('workFolder') and args.get('loginToShow'):
        if row[1]:
            make_tarfile(share_path + row[2] + '/' + args.get('workFolder') + '.tar.gz',
                         dir_path + actual_path + args.get('workFolder'))
        elif not row[1]:
            make_tarfile(share_path + row[2] + '/' + args.get('workFolder') + '.tar.gz',
                         row[0] + '/' + actual_path + args.get('workFolder'))
        cursor.execute('''INSERT INTO file_sharing(file_name, file_owner, file_short_name, login_to_show, password) 
                                    VALUES (?, ?, ?, ?, ?)''', (args.get('workFolder') + '.tar.gz', row[2],
                                                                rand_name, args.get('loginToShow'),
                                                                hash_perso(args.get('password'))))
        con.commit()
        return render_template("redirect/r-myfile-clipboardcopy.html", short_name=rand_name,
                               path="/my/file/?path=" + actual_path)

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
                    new_uuid = str(uuid.uuid3(uuid.uuid1(), str(uuid.uuid1())))
                    cursor.execute('''INSERT INTO user(token, user_name, password, admin, work_Dir) VALUES (?, ?, ?, 
                            ?, ?)''', (new_uuid, request.form['uname'], hash_perso(request.form['pword2']), admin,
                                       dir_path + '/' + secure_filename(request.form['uname'])))
                    con.commit()
                    os.mkdir(dir_path + '/' + secure_filename(request.form['uname']))
                    make_log('add_user', request.remote_addr, request.cookies.get('userID'), 2,
                             'Created user token: ' + new_uuid)
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


@app.route('/file_share/<short_name>')
def file_share(short_name=None):
    cursor.execute('''SELECT * FROM file_sharing WHERE file_short_name=?''', (short_name,))
    row = cursor.fetchone()
    is_login = user_login()
    if row[4]:
        if is_login[0]:
            return send_from_directory(directory=share_path + '/' + row[2], path=row[1])
        elif is_login == 'UserNotFound':
            return url_for('login')

    elif not row[4]:
        if not row[5]:
            return send_from_directory(directory=share_path + '/' + row[2], path=row[1])
        elif row[5] != "" and request.args.get('password') != "":
            if hash_perso(request.args.get('password')) == row[5]:
                return send_from_directory(directory=share_path + '/' + row[2], path=row[1])
            else:
                return render_template('redirect/r-share-file-with-password.html', short_name=short_name)
        elif row[5] != "" and request.args.get('password') == "":
            return render_template('redirect/r-share-file-with-password.html', short_name=short_name)


@app.route('/admin/show_share_file/')
@app.route('/admin/show_share_file/<random_name>')
def admin_show_share_file(random_name=None):
    admin_and_login = user_login()
    if admin_and_login[0] and admin_and_login[1]:
        cursor.execute('''SELECT user_name FROM user WHERE token=?''', (request.cookies.get('userID'),))
        user_name = cursor.fetchone()
        try:
            if random_name:
                cursor.execute('''SELECT file_name, file_owner FROM file_sharing WHERE file_short_name=?''',
                               (random_name,))
                row = cursor.fetchone()
                os.remove(share_path + row[1] + '/' + row[0])
                cursor.execute('''DELETE FROM file_sharing WHERE file_short_name = ?;''', (random_name,))
                con.commit()
        except Exception as e:
            make_log('error', request.remote_addr, request.cookies.get('userID'), 2, str(e))
        cursor.execute('''SELECT * FROM file_sharing''')
        all_share_file = cursor.fetchall()

        return render_template('admin/show_share_file.html', user_name=user_name, all_share_file=all_share_file)

    else:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2)
        return redirect(url_for('home'))


@app.route('/admin/api_manager/')
@app.route('/admin/api_manager/<api_id>')
def admin_api_manager(api_id=None):
    admin_and_login = user_login()
    if admin_and_login[0] and admin_and_login[1]:
        if api_id:
            cursor.execute('''SELECT * FROM api WHERE ID=?''', (api_id,))
            api = cursor.fetchall()
            return render_template('admin/specific_api_manager.html', api=api[0])
        else:
            cursor.execute('''SELECT * FROM api''')
            api = cursor.fetchall()
            cursor.execute('''SELECT user_name FROM user WHERE token=?''', (request.cookies.get('userID'),))
            user_name = cursor.fetchall()
            return render_template('admin/api_manager.html', user_name=user_name, api=api)
    else:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2)
        return redirect(url_for('home'))


@app.route('/admin/add_api/', methods=['POST', 'GET'])
def admin_add_api():
    api_create_file, api_upload_file, api_delete_file, api_create_folder, api_delete_folder, api_share_file_folder, \
        api_delete_share_file_folder, api_delete_user, api_create_user = 0, 0, 0, 0, 0, 0, 0, 0, 0
    admin_and_login = user_login()
    if admin_and_login[0] and admin_and_login[1]:
        if request.method == 'GET':
            cursor.execute('''SELECT user_name FROM user WHERE token=?''', (request.cookies.get('userID'),))
            user_name = cursor.fetchall()
            return render_template('admin/add_api.html', user_name=user_name)
        elif request.method == 'POST':
            if request.form.get('api_create_file'):
                api_create_file = 1
            if request.form.get('api_upload_file'):
                api_upload_file = 1
            if request.form.get('api_delete_file'):
                api_delete_file = 1
            if request.form.get('api_create_folder'):
                api_create_folder = 1
            if request.form.get('api_delete_folder'):
                api_delete_folder = 1
            if request.form.get('api_share_file_folder'):
                api_share_file_folder = 1
            if request.form.get('api_delete_share_file_folder'):
                api_delete_share_file_folder = 1
            if request.form.get('api_create_user'):
                api_create_user = 1
            if request.form.get('api_delete_user'):
                api_delete_user = 1

            new_uuid = str(uuid.uuid3(uuid.uuid1(), str(uuid.uuid1())))
            cursor.execute('''INSERT INTO api(token, api_name, api_desc, owner) VALUES (?, ?, ?, ?)''',
                           (new_uuid, request.form.get('api-name'), request.form.get('api-desc'),
                            request.cookies.get('userID')))
            cursor.execute('''INSERT INTO api_permission(token_api, create_file, upload_file, delete_file, 
            create_folder, delete_folder, share_file_and_folder, delete_share_file_and_folder, create_user, 
            delete_user) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (new_uuid, api_create_file, api_upload_file,
                                                                    api_delete_file, api_create_folder,
                                                                    api_delete_folder, api_share_file_folder,
                                                                    api_delete_share_file_folder, api_create_user,
                                                                    api_delete_user))
            con.commit()
            make_log('add_api', request.remote_addr, request.cookies.get('userID'), 2,
                     'Created API token: ' + new_uuid)
            return redirect(url_for('admin_api_manager'))
    else:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2)
        return redirect(url_for('home'))


########################################################################################################################
#                                         ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄                                        #
#                                        ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌                                       #
#                                        ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌ ▀▀▀▀█░█▀▀▀▀                                        #
#                                        ▐░▌       ▐░▌▐░▌       ▐░▌     ▐░▌                                            #
#                                        ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌     ▐░▌                                            #
#                                        ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌     ▐░▌                                            #
#                                        ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀      ▐░▌                                            #
#                                        ▐░▌       ▐░▌▐░▌               ▐░▌                                            #
#                                        ▐░▌       ▐░▌▐░▌           ▄▄▄▄█░█▄▄▄▄                                        #
#                                        ▐░▌       ▐░▌▐░▌          ▐░░░░░░░░░░░▌                                       #
#                                         ▀         ▀  ▀            ▀▀▀▀▀▀▀▀▀▀▀                                        #
########################################################################################################################


@app.route('/api/v1/test_connection', methods=['GET'])
def test_connection():
    content = request.json
    cursor.execute('''SELECT * FROM api where token=?''', (content['api-token'],))
    row1 = cursor.fetchone()
    make_log('test_connection', request.remote_addr, content['api-token'], 4, content['api-token'])
    return jsonify({
        "status-code": "200",
        "api-id": row1[0],
        "api-token": content['api-token'],
        "api-name": row1[2],
        "api-desc": row1[3],
        "owner": row1[4],
    })


@app.route('/api/v1/show_permission', methods=['GET'])
def show_permission():
    content = request.json
    cursor.execute('''SELECT * FROM api where token=?''', (content['api-token'],))
    row1 = cursor.fetchone()
    cursor.execute('''SELECT * FROM api_permission where token_api=?''', (content['api-token'],))
    row2 = cursor.fetchone()
    make_log('show_permission', request.remote_addr, content['api-token'], 4, content['api-token'])

    return jsonify({
        "status-code": "200",
        "api-token": content['api-token'],
        "api-name": row1[2],
        "permission": {
            "create_file": row2[1],
            "upload_file": row2[2],
            "delete_file": row2[3],
            "create_folder": row2[4],
            "delete_folder": row2[5],
            "share_file_and_folder": row2[6],
            "delete_share_file_and_folder": row2[7],
            "create_user": row2[8],
            "delete_user": row2[9],
        }
    })


@app.route('/api/v1/add_user', methods=['POST'])
def add_user_api():
    admin = False
    content = request.json
    cursor.execute('''SELECT * FROM api where token=?''', (content['api-token'],))
    row1 = cursor.fetchone()
    cursor.execute('''SELECT * FROM api_permission where token_api=?''', (content['api-token'],))
    row2 = cursor.fetchone()
    if row2[8]:
        try:
            new_uuid = str(uuid.uuid3(uuid.uuid1(), str(uuid.uuid1())))
            if content['admin'] == 1:
                admin = True

            cursor.execute('''INSERT INTO user(token, user_name, password, admin, work_Dir) 
                            VALUES (?, ?, ?, ?, ?)''', (new_uuid, content['username'], hash_perso(content['password']),
                                                        admin, dir_path + '/' + secure_filename(content['username'])))
            con.commit()
            make_log('add_user_api', request.remote_addr, request.cookies.get('userID'), 4,
                     'Created User token: ' + new_uuid, content['api-token'])
            return jsonify({
                "status-code": "200",
                "api-token": content['api-token'],
                "user-to-create": content['username'],
                "user-passsword-to-create": content['password'],
                "user-permission-to-create": content['admin'],
                "user-token-create": new_uuid
            })
        except KeyError as e:
            return 'L\'argument {} est manquant!'.format(str(e))
    else:
        if row1:
            make_log('add_api_error', request.remote_addr, content['api-token'], 4,
                     'Not enough permission', content['api-token'])
            return jsonify({
                "status-code": "401",
                "details": "You don't have the permission to use that"
            })
        else:
            make_log('add_api_error', request.remote_addr, content['api-token'], 4,
                     'Not logged in', content['username'])
            return jsonify({
                "status-code": "401",
                "details": "You must be login to use that"
            })


if __name__ == '__main__':
    app.run()

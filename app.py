from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, url_for, redirect, make_response, send_from_directory, jsonify, \
    escape
from time import sleep
from argon2 import argon2_hash
from datetime import datetime
from os import path, getcwd, walk, remove, system, mkdir
from subprocess import check_output
from uuid import uuid1, uuid3
from shutil import rmtree, copy2
from random import choices
from string import ascii_lowercase
from tarfile import open as tar_open
from json import load
from hashlib import sha256, new
from Utils.database import DataBase


def f_user_name(user_id):
    data = database.select("""SELECT user_name FROM cantina_administration.user WHERE token=%s""", (user_id,), 1)
    return data[0]


def salt_password(passwordtohash, user_name, new_account=False):
    try:
        if not new_account:
            try:
                data = database.select('''SELECT salt FROM cantina_administration.user WHERE user_name=%s''',
                                       (user_name,), 1)
                passw = sha256(argon2_hash(passwordtohash, data[0])).hexdigest().encode()
                return passw
            except Exception as e:
                return 'User Not Found, ' + str(e)
        else:
            passw = sha256(argon2_hash(passwordtohash, user_name)).hexdigest().encode()
            return passw

    except AttributeError as error:
        make_log('Error', request.remote_addr, request.cookies.get('userID'), 2, str(error))
        return None


def user_login():
    data = database.select('''SELECT user_name, admin FROM cantina_administration.user WHERE token = %s''',
                           (request.cookies.get('userID'),), 1)
    try:
        if data[0] != '' and data[1]:
            return True, True
        elif data[0] != '' and not data[1]:
            return True, False
        else:
            return False, False
    except Exception as error:
        return error


def make_log(action_name, user_ip, user_token, log_level, argument=None, content=None):
    if content:
        database.insert('''INSERT INTO cantina_administration.log(name, user_ip, user_token, argument, log_level) 
        VALUES (%s, %s, %s,%s,%s)''', (str(action_name), str(user_ip), str(content), argument, log_level))
    else:
        database.insert('''INSERT INTO cantina_administration.log(name, user_ip, user_token, argument, log_level) 
        VALUES (%s, %s, %s,%s,%s)''', (str(action_name), str(user_ip), str(user_token), argument, log_level))


def make_tarfile(output_filename, source_dir):
    with tar_open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=path.basename(source_dir))


fd, filenames, lastPath = "", "", ""
dir_path = path.abspath(getcwd()) + '/file_cloud'
share_path = path.abspath(getcwd()) + '/share'
app = Flask(__name__)
app.config['UPLOAD_PATH'] = dir_path
api_no_token = 'You must send a token in JSON with the name: `api-token`!'
conf_file = open(path.abspath(getcwd()) + "/config.json", 'r')
config_data = load(conf_file)

# Connection aux bases de données
database = DataBase(user=config_data['database'][0]['database_username'],
                    password=config_data['database'][0]['database_password'], host="localhost", port=3306)

try:
    database.connection()
except Exception as e:
    print("Erreur de connection à MySQL... Tentative de reconnexion dans 5 minutes...\n" + str(e))
    sleep(250)
    try:
        database.connection()
    except Exception as e:
        print(e)
        exit(0)

# Creation des tables des bases données
database.create_table(
    "CREATE TABLE IF NOT EXISTS cantina_administration.user(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT,  "
    "user_name TEXT, salt TEXT, password TEXT, admin BOOL, work_Dir TEXT, last_online TEXT)")
database.create_table(
    "CREATE TABLE IF NOT EXISTS cantina_administration.log(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, name TEXT,  "
    "user_ip text, user_token TEXT, argument TEXT, log_level INT, date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
database.create_table(
    "CREATE TABLE IF NOT EXISTS cantina_administration.file_sharing(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, "
    "file_name TEXT, file_owner text, file_short_name TEXT, login_to_show BOOL DEFAULT 1, password TEXT, "
    "date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
database.create_table(
    "CREATE TABLE IF NOT EXISTS cantina_administration.api(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, "
    "api_name TEXT, api_desc TEXT, owner TEXT)")
database.create_table(
    "CREATE TABLE IF NOT EXISTS cantina_administration.api_permission(token_api TEXT, create_file BOOL, upload_file "
    "BOOL, delete_file BOOL, create_folder BOOL, delete_folder BOOL, share_file_and_folder BOOL, "
    "delete_share_file_and_folder BOOL, create_user BOOL, delete_user BOOL)")


# Fonction définissant la racine de Cantina Cloud
@app.route('/')
def home():
    if not request.cookies.get('userID'):
        return redirect(url_for('login'))
    data = database.select('''SELECT user_name, admin FROM cantina_administration.user WHERE token = %s''',
                           (request.cookies.get('userID'),), 1)
    try:
        return render_template('home.html', cur=data)
    except IndexError:
        return redirect(url_for('login'))


# Fonction permettant de voire les fichiers de Cantina Cloud
@app.route('/file/')
def file():
    global filenames, lastPath, fd
    actual_path, lastPath, rand_name = '/', '/', ''
    args = request.args
    work_file_in_dir, work_dir = [], []
    git_repo = False
    user_token = request.cookies.get('userID')

    # Redirection vers la connection si l'utilisateur n'est pas connecté
    if not user_token:
        return redirect(url_for('login'))

    for i in choices(ascii_lowercase, k=10):
        rand_name += i

    row = database.select(f'''SELECT work_Dir, admin, user_name FROM cantina_administration.user WHERE token = %s''',
                          (user_token,), 1)
    print(dir_path)
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
                if '.git' in dirnames:
                    git_repo = True
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break
        elif not row[1]:
            for (dirpath, dirnames, filenames) in walk(row[0] + args.get('path')):
                if '.git' in dirnames:
                    git_repo = True
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break

    if not args.get('action') or args.get('action') == 'show':
        print(actual_path, work_dir, work_file_in_dir)
        return render_template('myfile.html', dir=work_dir, file=work_file_in_dir, path=actual_path,
                               lastPath=lastPath, git_repo=git_repo)

    elif args.get('action') == "deleteFile" and args.get('workFile') and args.get('workFile') in filenames:
        if row[1]:
            remove(dir_path + actual_path + secure_filename(args.get('workFile')))
        elif not row[1]:
            remove(row[0] + '/' + actual_path + secure_filename(args.get('workFile')))
        return render_template("redirect/r-myfile.html", path="/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "createFile" and args.get('workFile'):
        if row[1]:
            fd = open(dir_path + args.get('path') + "/" + secure_filename(args.get('workFile')), 'r')
        elif not row[1]:
            fd = open(row[0] + '/' + args.get('path') + "/" + secure_filename(args.get('workFile')), 'r')

        fd.close()
        return render_template("redirect/r-myfile.html", path="/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "cloneRepo" and args.get('repoLink'):
        if row[1]:
            system("cd " + dir_path + args.get('path') + "/ && git clone " + args.get('repoLink'))
        elif not row[1]:
            system("cd " + row[0] + '/' + args.get('path') + "/ && git clone " + args.get('repoLink'))

        return render_template("redirect/r-myfile.html", path="/file/%spath=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "pullRepo" and git_repo:
        if row[1]:
            system("cd " + dir_path + args.get('path') + "/ && git pull")
        elif not row[1]:
            system("cd " + row[0] + '/' + args.get('path') + "/ && git pull")

        return render_template("redirect/r-myfile.html", path="/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "deleteFolder" and args.get('workFile') and args.get('workFile') in work_dir:
        if row[1]:
            rmtree(dir_path + actual_path + "/" + args.get('workFile'))
        elif not row[1]:
            rmtree(row[0] + '/' + actual_path + args.get('workFile'))

        return render_template("redirect/r-myfile.html", path="/file/?path=" + actual_path)

    elif args.get('action') == "createFolder" and args.get('workFile'):
        if row[1]:
            mkdir(dir_path + actual_path + args.get('workFile'))
        elif not row[1]:
            mkdir(row[0] + '/' + actual_path + args.get('workFile'))
        return render_template("redirect/r-myfile.html", path="/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "shareFile" and args.get('workFile') and args.get('loginToShow'):
        if row[1]:
            copy2(dir_path + actual_path + args.get('workFile'), share_path + '/' + row[2] + '/' + args.get('workFile'))
        elif not row[1]:
            copy2(row[0] + '/' + actual_path + args.get('workFile'), share_path + row[2] + '/' + args.get('workFile'))
        if args.get('loginToShow') == '0':
            database.insert('''INSERT INTO cantina_cloud.file_sharing(file_name, file_owner, file_short_name, 
            login_to_show, password) VALUES (%s, %s, %s, %s, %s)''', (args.get('workFile'), row[2], rand_name,
                                                                      args.get('loginToShow'), None))

        elif args.get('loginToShow') == '1':
            database.insert('''INSERT INTO cantina_cloud.file_sharing(file_name, file_owner, file_short_name, 
            login_to_show, password) VALUES (%s, %s, %s, %s, %s)''', (args.get('workFile'), row[2], rand_name,
                                                                      args.get('loginToShow'), salt_password(
                args.get('password'), row[2])))

        return render_template("redirect/r-myfile-clipboardcopy.html", short_name=rand_name,
                               path="/file/?path=" + actual_path)

    elif args.get('action') == "shareFolder" and args.get('workFolder') and args.get('loginToShow'):
        if row[1]:
            make_tarfile(share_path + '/' + row[2] + '/' + args.get('workFolder') + '.tar.gz',
                         dir_path + actual_path + args.get('workFolder'))
        elif not row[1]:
            make_tarfile(share_path + '/' + row[2] + '/' + args.get('workFolder') + '.tar.gz',
                         row[0] + '/' + actual_path + args.get('workFolder'))
        database.insert('''INSERT INTO cantina_cloud.file_sharing(file_name, file_owner, file_short_name, login_to_show, 
        password) VALUES (%s, %s, %s, %s, %s)''', (args.get('workFolder') + '.tar.gz', row[2], rand_name,
                                                   args.get('loginToShow'),
                                                   salt_password(args.get('password'), row[2])))
        return render_template("redirect/r-myfile-clipboardcopy.html", short_name=rand_name,
                               path="/file/?path=" + actual_path)

    else:
        return render_template('myfile.html', dir=work_dir, file=work_file_in_dir, path=args.get('path') + "/",
                               lastPath=lastPath)


# Fonction permettant d'upload un fichier dans le dossier dans lequelle on est
@app.route('/file/upload', methods=['GET', 'POST'])
def upload_file():
    args = request.args

    if request.method == 'GET':
        return render_template('upload_file.html')

    elif request.method == 'POST':
        user_token = request.cookies.get('userID')
        user_check = user_login()

        if user_check == 'UserNotFound':
            return redirect(url_for('login'))
        elif user_check[1]:
            f = request.files['file']
            f.save(path.join(dir_path + args.get('path'), secure_filename(f.filename)))
            make_log('upload_file', request.remote_addr, request.cookies.get('userID'), 1,
                     path.join(dir_path + args.get('path'), secure_filename(f.filename)))
            return redirect(url_for('file', path=args.get('path')))
        elif not user_check[1]:
            f = request.files['file']
            f.save(path.join(dir_path + '/' + f_user_name(user_token) + args.get('path'),
                             secure_filename(f.filename)))
            make_log('upload_file', request.remote_addr, request.cookies.get('userID'), 1,
                     path.join(dir_path + args.get('path'), secure_filename(f.filename)))
            return redirect(url_for('file', path=args.get('path')))


# Fonction permettant de télécharger le fichier sélectionné
@app.route('/file/download')
def download_file():
    args = request.args

    user_token = request.cookies.get('userID')
    user_check = user_login()

    make_log('Download file', request.remote_addr, request.cookies.get('userID'), 1,
             dir_path + args.get('path') + args.get('item'))
    if user_check == 'UserNotFound':
        return redirect(url_for('login'))
    elif user_check[1]:
        return send_from_directory(secure_filename(dir_path + args.get('path')), path=args.get('item'))
    elif not user_check[1]:
        return send_from_directory(secure_filename(dir_path + '/' + f_user_name(user_token) + args.get('path')),
                                   path=args.get('item'))


# Fonction permettant de voire les fichiers partagé
@app.route('/file_share/<short_name>')
def file_share(short_name=None):
    row = database.select('''SELECT * FROM cantina_cloud.file_sharing WHERE file_short_name=%s''', (short_name,), 1)
    is_login = user_login()
    if not row[4]:
        if not row[5]:
            return send_from_directory(directory=share_path + '/' + row[2], path=row[1])
        elif row[5] != "" and request.args.get('password') != "":
            data = database.select('''SELECT salt FROM cantina_administration.user WHERE user_name=%s''', (row[2],), 1)
            if salt_password(request.args.get('password'), data) == row[5]:
                return send_from_directory(directory=share_path + '/' + row[2], path=row[1])
            else:
                return render_template('redirect/r-share-file-with-password.html', short_name=short_name)
        elif row[5] != "" and request.args.get('password') == "":
            return render_template('redirect/r-share-file-with-password.html', short_name=short_name)

    elif row[4]:
        if is_login[0]:
            return send_from_directory(directory=share_path + '/' + row[2], path=row[1])
        elif is_login == 'UserNotFound':
            return url_for('login')


# Fonction permettant de se connecter à Cantina Cloud
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
        passwd = request.form['passwd']
        row = database.select(f'''SELECT user_name, password, token FROM cantina_administration.user WHERE password = %s 
        AND user_name = %s''', (salt_password(passwd, user), user), 1)

        try:
            make_log('login', request.remote_addr, row[2], 1)
            resp = make_response(redirect(url_for('home')))
            resp.set_cookie('userID', row[2])
            database.insert('''UPDATE cantina_administration.user SET last_online=%s WHERE token=%s''',
                            (datetime.now(), row[2]))
            return resp
        except Exception as error:
            make_log('Error', request.remote_addr, request.cookies.get('userID'), 2, str(error))
            return redirect(url_for("home"))

    elif request.method == 'GET':
        return render_template('login.html')


# Fonction permettant de se déconnecter de Cantina Cloud
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    make_log('logout', request.remote_addr, request.cookies.get('userID'), 1)
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('userID', '', expires=0)
    return resp


# Fonction permettant de voire la page 'principale' du panel Admin de Cantina Cloud 
@app.route('/admin/home')
def admin_home():
    try:
        count = 0
        admin_and_login = user_login()
        if admin_and_login[0] and admin_and_login[1]:
            for root_dir, cur_dir, files in walk(dir_path):
                count += len(files)
            main_folder_size = check_output(['du', '-sh', dir_path]).split()[0].decode('utf-8')
            user_name = database.select('''SELECT user_name FROM cantina_administration.user WHERE token=%s''',
                                        (request.cookies.get('userID'),))
            return render_template('admin/home.html', data=user_name, file_number=count,
                                   main_folder_size=main_folder_size)
        else:
            return redirect(url_for('home'))

    except Exception as error:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2, str(error))
        return redirect(url_for('home'))


# Fonction permettant de visualiser les utilisateur de Cantina Cloud
@app.route('/admin/usermanager/')
@app.route('/admin/usermanager/<user_name>')
def admin_show_user(user_name=None):
    try:
        admin_and_login = user_login()
        if admin_and_login[0] and admin_and_login[1]:
            if user_name:
                user_account = database.select('''SELECT * FROM cantina_administration.user WHERE user_name=%s''',
                                               (user_name,))

                return render_template('admin/specific_user_manager.html', user_account=user_account[0])
            else:
                all_account = database.select(body='''SELECT * FROM cantina_administration.user''')
                user_name = database.select('''SELECT user_name FROM cantina_administration.user WHERE token=%s''',
                                            (request.cookies.get('userID'),))
                return render_template('admin/user_manager.html', user_name=user_name,
                                       all_account=all_account)
        else:
            return redirect(url_for('home'))
    except Exception as error:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2, str(error))
        return redirect(url_for('home'))


# Fonction permettant de créer un utilisateur
@app.route('/admin/add_user/', methods=['POST', 'GET'])
def admin_add_user():
    try:
        admin = 0
        admin_and_login = user_login()
        if admin_and_login[0] and admin_and_login[1]:
            if request.method == 'GET':
                user_name = database.select('''SELECT user_name FROM cantina_administration.user WHERE token=%s''',
                                            (request.cookies.get('userID'),))
                return render_template('admin/add_user.html', user_name=user_name)
            elif request.method == 'POST':

                if request.form['pword1'] == request.form['pword2']:
                    data = request.form
                    new_uuid = str(uuid3(uuid1(), str(uuid1())))
                    new_salt = new('sha256').hexdigest()
                    try:
                        for i in data:
                            if i == 'admin':
                                admin = 1
                            else:
                                pass

                        database.insert('''INSERT INTO cantina_administration.user(token, user_name, salt, password, 
                        admin, work_Dir) VALUES (%s, %s, %s, %s, %s, %s)''',
                                        (new_uuid, request.form['uname'], new_salt,
                                         salt_password(request.form['pword2'], new_salt, new_account=True), admin,
                                         dir_path + '/' + secure_filename(request.form['uname'])))

                    except Exception as error:
                        make_log('Error', request.remote_addr, request.cookies.get('userID'), 2, str(error))

                    mkdir(dir_path + '/' + secure_filename(request.form['uname']))
                    mkdir(share_path + '/' + secure_filename(request.form['uname']))
                    make_log('add_user', request.remote_addr, request.cookies.get('userID'), 2,
                             'Created user token: ' + new_uuid)
                    return redirect(url_for('admin_show_user'))
    except Exception as error:
        make_log('Error', request.remote_addr, request.cookies.get('userID'), 2, str(error))
        return redirect(url_for('home'))


# Fonction permettant de voire les logs générer par Cantina Cloud
@app.route('/admin/show_log/')
@app.route('/admin/show_log/<log_id>')
def admin_show_log(log_id=None):
    try:
        admin_and_login = user_login()
        if admin_and_login[0] and admin_and_login[1]:
            if log_id:
                log = database.select('''SELECT * FROM cantina_administration.log WHERE ID=%s''', (log_id,), 1)
                return render_template('admin/specific_log.html', log=log)
            else:
                all_log = database.select('''SELECT * FROM cantina_administration.log''')
                return render_template('admin/show_log.html', all_log=all_log)
    except Exception as error:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2, str(error))
        return redirect(url_for('home'))


# Fonction permettant de voire tout les fichiers partagé
@app.route('/admin/show_share_file/')
@app.route('/admin/show_share_file/<random_name>')
def admin_show_share_file(random_name=None):
    admin_and_login = user_login()
    if admin_and_login[0] and admin_and_login[1]:
        user_name = database.select('''SELECT user_name FROM cantina_administration.user WHERE token=%s''',
                                    (request.cookies.get('userID'),), 1)
        try:
            row = database.select('''SELECT file_name, file_owner FROM cantina_cloud.file_sharing WHERE 
            file_short_name=%s''', (random_name,), 1)
            if random_name:
                remove(share_path + '/' + row[1] + '/' + row[0])
                database.insert('''DELETE FROM cantina_cloud.file_sharing WHERE file_short_name = %s;''', (random_name,)
                                )
        except Exception as error:
            make_log('Error', request.remote_addr, request.cookies.get('userID'), 2, str(error))
        all_share_file = database.select('''SELECT * FROM cantina_cloud.file_sharing''')
        return render_template('admin/show_share_file.html', user_name=user_name, all_share_file=all_share_file)

    else:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2)
        return redirect(url_for('home'))


# Fonction permettant de voire les API créer sur Cantina Cloud
@app.route('/admin/api_manager/')
@app.route('/admin/api_manager/<api_id>')
def admin_api_manager(api_id=None):
    admin_and_login = user_login()
    if admin_and_login[0] and admin_and_login[1]:
        if api_id:
            api = database.select('''SELECT * FROM cantina_cloud.api WHERE ID=%s''', (api_id,))
            return render_template('admin/specific_api_manager.html', api=api[0])
        else:
            api = database.select('''SELECT * FROM cantina_cloud.api''')
            return render_template('admin/api_manager.html', api=api)
    else:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2)
        return redirect(url_for('home'))


# Fonction permettant de créer une API Cantina Cloud
@app.route('/admin/add_api/', methods=['POST', 'GET'])
def admin_add_api():
    api_create_file, api_upload_file, api_delete_file, api_create_folder, api_delete_folder, api_share_file_folder, \
        api_delete_share_file_folder, api_delete_user, api_create_user = 0, 0, 0, 0, 0, 0, 0, 0, 0
    admin_and_login = user_login()
    if admin_and_login[0] and admin_and_login[1]:
        if request.method == 'GET':
            user_name = database.select('''SELECT user_name FROM cantina_administration.user WHERE token=%s''',
                                        (request.cookies.get('userID'),))

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

            new_uuid = str(uuid3(uuid1(), str(uuid1())))
            database.insert('''INSERT INTO cantina_cloud.api(token, api_name, api_desc, owner) VALUES (%s, %s, %s, 
            %s)''', (new_uuid, request.form.get('api-name'), request.form.get('api-desc'), request.cookies.get(
                'userID')))
            database.insert('''INSERT INTO cantina_cloud.api_permission(token_api, create_file, upload_file, 
            delete_file, create_folder, delete_folder, share_file_and_folder, delete_share_file_and_folder, 
            create_user, delete_user) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (new_uuid, api_create_file,
                                                                                           api_upload_file,
                                                                                           api_delete_file,
                                                                                           api_create_folder,
                                                                                           api_delete_folder,
                                                                                           api_share_file_folder,
                                                                                           api_delete_share_file_folder,
                                                                                           api_create_user,
                                                                                           api_delete_user))

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
    row1 = database.select('''SELECT * FROM cantina_cloud.api where token=%s''', (escape(content['api-token']),), 1)
    make_log('test_connection', request.remote_addr, content['api-token'], 4, content['api-token'])
    return jsonify({
        "status-code": "200",
        "api-id": row1[0],
        "api-token": escape(content['api-token']),
        "api-name": row1[2],
        "api-desc": row1[3],
        "owner": row1[4],
    })


@app.route('/api/v1/show_permission', methods=['GET'])
def show_permission():
    content = request.json
    row1 = database.select('''SELECT * FROM cantina_cloud.api where token=%s''', (escape(content['api-token']),), 1)
    row2 = database.select('''SELECT * FROM cantina_cloud.api_permission where token_api=%s''',
                           (escape(content['api-token']),), 1)
    make_log('show_permission', request.remote_addr, escape(content['api-token']), 4, escape(content['api-token']))

    return jsonify({
        "status-code": "200",
        "api-token": escape(content['api-token']),
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
    row1 = database.select('''SELECT * FROM cantina_cloud.api where token=%s''', (escape(content['api-token']),), 1)
    row2 = database.select('''SELECT * FROM cantina_cloud.api_permission where token_api=%s''',
                           (escape(content['api-token']),), 1)
    if row2[8]:
        try:
            new_salt = new('sha256').hexdigest()
            new_uuid = str(uuid3(uuid1(), str(uuid1())))
            if content['admin'] == 1:
                admin = True

            database.insert('''INSERT INTO cantina_administration.user(token, user_name, salt, password, admin, 
            work_Dir)  VALUES (%s, %s, %s, %s, %s, %s)''', (new_uuid, escape(content['username']), new_salt,
                                                            salt_password(content['password'], new_salt), admin,
                                                            dir_path + '/' + secure_filename(content['username'])))
            make_log('add_user_api', request.remote_addr, request.cookies.get('userID'), 4,
                     'Created User token: ' + new_uuid, escape(content['api-token']))
            return jsonify({
                "status-code": "200",
                "api-token": escape(content['api-token']),
                "user-to-create": escape(content['username']),
                "user-passsword-to-create": escape(content['password']),
                "user-permission-to-create": escape(content['admin']),
                "user-token-create": new_uuid
            })
        except KeyError as error:
            return 'L\'argument {} est manquant!'.format(str(error))
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


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404


if __name__ == '__main__':
    app.run(port=config_data['port'])

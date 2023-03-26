from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, url_for, redirect, jsonify, escape
from time import sleep
from os import path, getcwd, remove
from uuid import uuid1, uuid3
from json import load
from hashlib import new
from Utils.database import DataBase
from Utils.utils import salt_password, user_login, make_log
from Cogs.home import home_cogs
from Cogs.file import file_cogs
from Cogs.upload_file import upload_file_cogs
from Cogs.download_file import download_file_cogs
from Cogs.file_share import file_share_cogs
from Cogs.login import login_cogs
from Cogs.logout import logout_cogs
from Cogs.admin.home import home_admin_cogs
from Cogs.admin.show_user import show_user_cogs
from Cogs.admin.add_user import add_user_cogs

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
    return home_cogs(request, database)


# Fonction permettant de voire les fichiers de Cantina Cloud
@app.route('/file/')
def file():
    return file_cogs(request, database, share_path=share_path, dir_path=dir_path)


# Fonction permettant d'upload un fichier dans le dossier dans lequelle on est
@app.route('/file/upload', methods=['GET', 'POST'])
def upload_file():
    return upload_file_cogs(request, database, dir_path)


# Fonction permettant de télécharger le fichier sélectionné
@app.route('/file/download')
def download_file():
    return download_file_cogs(request, database, dir_path)


# Fonction permettant de voire les fichiers partagé
@app.route('/file_share/<short_name>')
def file_share(short_name=None):
    return file_share_cogs(request, database, share_path, short_name)


# Fonction permettant de se connecter à Cantina Cloud
@app.route('/login', methods=['POST', 'GET'])
def login():
    return login_cogs(request, database)


# Fonction permettant de se déconnecter de Cantina Cloud
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    return logout_cogs(request, database)


# Fonction permettant de voire la page 'principale' du panel Admin de Cantina Cloud 
@app.route('/admin/home')
def admin_home():
    return home_admin_cogs(request, database, dir_path)


# Fonction permettant de visualiser les utilisateur de Cantina Cloud
@app.route('/admin/usermanager/')
@app.route('/admin/usermanager/<user_name>')
def admin_show_user(user_name=None):
    return show_user_cogs(request, database, user_name)


# Fonction permettant de créer un utilisateur
@app.route('/admin/add_user/', methods=['POST', 'GET'])
def admin_add_user():
    return add_user_cogs(request, database, dir_path, share_path)


# Fonction permettant de voire les logs générer par Cantina Cloud
@app.route('/admin/show_log/')
@app.route('/admin/show_log/<log_id>')
def admin_show_log(log_id=None):
    try:
        admin_and_login = user_login(database, request)
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
    admin_and_login = user_login(database, request)
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
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2, database)
        return redirect(url_for('home'))


# Fonction permettant de voire les API créer sur Cantina Cloud
@app.route('/admin/api_manager/')
@app.route('/admin/api_manager/<api_id>')
def admin_api_manager(api_id=None):
    admin_and_login = user_login(database, request)
    if admin_and_login[0] and admin_and_login[1]:
        if api_id:
            api = database.select('''SELECT * FROM cantina_cloud.api WHERE ID=%s''', (api_id,))
            return render_template('admin/specific_api_manager.html', api=api[0])
        else:
            api = database.select('''SELECT * FROM cantina_cloud.api''')
            return render_template('admin/api_manager.html', api=api)
    else:
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2, database)
        return redirect(url_for('home'))


# Fonction permettant de créer une API Cantina Cloud
@app.route('/admin/add_api/', methods=['POST', 'GET'])
def admin_add_api():
    api_create_file, api_upload_file, api_delete_file, api_create_folder, api_delete_folder, api_share_file_folder, \
        api_delete_share_file_folder, api_delete_user, api_create_user = 0, 0, 0, 0, 0, 0, 0, 0, 0
    admin_and_login = user_login(database, request)
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
        make_log('login_error', request.remote_addr, request.cookies.get('userID'), 2, database)
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
                                                            salt_password(content['password'], new_salt, database,
                                                                          request),
                                                            admin,
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


@app.errorhandler(403)
def acces_denied(error):
    return render_template('error/403.html'), 403


if __name__ == '__main__':
    app.run(port=config_data['port'])

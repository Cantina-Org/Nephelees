from flask import Flask, render_template, request
from time import sleep
from os import path, getcwd
from json import load
from Utils.database import DataBase
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
from Cogs.admin.show_log import show_log_cogs
from Cogs.admin.show_share_file import show_share_file_cogs
from Cogs.admin.api_manager import api_manager_cogs
from Cogs.admin.add_api import add_api_cogs
from Cogs.api.test_connection import test_connection_cogs
from Cogs.api.show_permission import show_permission_cogs
from Cogs.api.add_user import add_user_api_cogs

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
@app.route('/login')
def login():
    return login_cogs(request, database)


# Fonction permettant de se déconnecter de Cantina Cloud
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    return logout_cogs(request, database)

###########################################
#                  API                    #
###########################################

@app.route('/api/v1/test_connection', methods=['GET'])
def test_connection():
    return test_connection_cogs(request, database)


@app.route('/api/v1/show_permission', methods=['GET'])
def show_permission():
    return show_permission_cogs(request, database)


@app.route('/api/v1/add_user', methods=['POST'])
def add_user_api():
    return add_user_api_cogs(request, database, dir_path)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404


@app.errorhandler(403)
def acces_denied(error):
    return render_template('error/403.html'), 403


if __name__ == '__main__':
    app.run(port=config_data['port'])

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
from Cogs.api.test_connection import test_connection_cogs
from Cogs.api.show_permission import show_permission_cogs
from Cogs.api.add_user import add_user_api_cogs

dir_path = path.abspath(getcwd()) + '/file_cloud'
share_path = path.abspath(getcwd()) + '/share'
app = Flask(__name__)
app.config['UPLOAD_PATH'] = dir_path
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


# Fonction définissant la racine de Cantina Cloud
@app.route('/')
def home():
    return home_cogs(request, database)


# Fonction permettant de voire les fichiers de Néphélées
@app.route('/file/')
def file():
    return file_cogs(request, database, share_path=share_path, dir_path=dir_path)


# Fonction permettant upload un fichier dans le dossier courant
@app.route('/file/upload', methods=['GET', 'POST'])
def upload_file():
    return upload_file_cogs(request, database, dir_path)


# Fonction permettant de télécharger le fichier sélectionné
@app.route('/file/download')
def download_file():
    return download_file_cogs(request, database, dir_path)


# Fonction permettant de voire les fichiers partagés
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
    print(error)
    return render_template('error/404.html'), 404


@app.errorhandler(403)
def access_denied(error):
    print(error)
    return render_template('error/403.html'), 403


if __name__ == '__main__':
    app.run(port=config_data['port'])

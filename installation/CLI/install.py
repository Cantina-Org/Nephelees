from hashlib import sha256
from json import dumps
from os import system, getuid
from platform import uname
from uuid import uuid1, uuid3
from argon2 import argon2_hash
from pymysql import connect


def salt_password(passwordtohash, user_name, new_account=False):
    try:
        if not new_account:
            pass
        else:
            passw = sha256(argon2_hash(passwordtohash, user_name)).hexdigest().encode()
            return passw

    except AttributeError as e:
        print(e)
        return None


CRED = '\033[91m'
CEND = '\033[0m'
CWAR = '\033[93m'
based_on = None
os_info = uname()
database = [False, False]

if getuid() != 0:
    exit("L'installation doit être faite avec les permissions d'administrateur!")
elif os_info.system != "Linux":
    exit("L'installation doit être faire sur une système linux!")

print("Bienvenue dans l'installation de Cantina Cloud!")

if "Debian" in os_info.version:
    print("Système Debian détecter.")
    system("sudo adduser cantina --system")
    system("sudo addgroup cantina")
else:
    distrib_check = input(
        "Votre système est:\n     1: Basé sur Debian\n     2: Basé sur Arch\n     3: Basé sur Red Hat\n")
    while distrib_check not in ["1", "2", "3"]:
        print("Merci de répondre uniquement par 1, 2 ou 3!")
        distrib_check = input(
            "Votre système est:\n     1: Basé sur Debian\n     2: Basé sur Arch\n     3: Basé sur Red Hat\n")

    if distrib_check == "1" or distrib_check == "3":
        system("sudo adduser cantina --system")
        system("sudo addgroup cantina")
    elif distrib_check == "2":
        system("sudo useradd cantina")
        system("sudo groupadd cantina")
    else:
        exit("Vous avez cassé notre système :/")

system("sudo usermod -a -G cantina cantina")
system("git clone https://github.com/Cantina-Org/Cloud /home/cantina/cloud")
system("mkdir /home/cantina/cloud/file_cloud /home/cantina/cloud/share")
system("python -m pip install -r requirements.txt")

print(CRED +
      "----------------------------------------------------------------------------------------------------------------"
      "--------------------------------------------------------" + CEND
      )

new_instance = input("Avez vous déjà installé sur ce serveur une projet Cantina? ")
while new_instance not in ['Oui', 'oui', 'o', 'Non', 'non', 'n']:
    print("Les réponses valides sont: 'Oui', 'oui', 'o' ou 'Non', 'non', 'n'")
    new_instance = input("Avez vous déjà installé un projet Cantina sur ce serveur? ")

if new_instance in ['Oui', 'oui', 'o']:
    print(CRED + "ATTENTION: " + CWAR + " si vous n'avez pas encore d'instance Cantina sur ce serveur, vous ne pourrez "
                                        "pas utiliser Cantina Cloud car aucun utilisateur ne sera créé!" + CEND)
    print("Identifiants de connexion aux bases de données: ")
    database_username = input("    Nom d'utilisateur: ")
    database_password = input("    Mots de passe: ")

    while database_password == '' or database_username == '':
        print("Merci de rentrer des valeurs!")
        database_username = input("    Nom d'utilisateur: ")
        database_password = input("    Mots de passe: ")

    try:
        con = connect(user=database_username, password=database_password, host="localhost", port=3306)
        cursor = con.cursor()

    except Exception as e:
        exit("Un problème est apparue lors de la connexion à Mariadb: " + str(e))

    cursor.execute("""SHOW DATABASES""")
    data = cursor.fetchall()

    for i in data:
        if i[0] == 'cantina_administration':
            database[0] = True
        elif i[0] == 'cantina_cloud':
            database[1] = True

    if not database[0] or not database[1]:
        exit("Merci de créer les bases de données!\n cantina_administration: " + str(database[0]) +
             "\ncantina_cloud: " + str(database[1]))

    try:
        cursor.execute("USE cantina_administration")
        cursor.execute("SELECT id, user_name FROM user")
        data_id = cursor.fetchall()

        for i in data_id:
            system("mkdir /home/cantina/cloud/file_cloud/{} /home/cantina/cloud/share/{}".format(i[1], i[1]))

    except Exception as e:
        exit('Une erreur est survenue lors de la récupération des utilisateur de la base de donnée: ' + str(e))

    cursor.execute("USE cantina_cloud")
    cursor.execute("CREATE TABLE IF NOT EXISTS file_sharing(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, file_name TEXT,"
                   " file_owner text, file_short_name TEXT, login_to_show BOOL DEFAULT 1, password TEXT,"
                   "date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS api(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, "
                   "api_name TEXT, api_desc TEXT, owner TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS api_permission(token_api TEXT, create_file BOOL, upload_file BOOL, "
                   "delete_file BOOL, create_folder BOOL, delete_folder BOOL, share_file_and_folder BOOL, "
                   "delete_share_file_and_folder BOOL, create_user BOOL, delete_user BOOL)")


elif new_instance in ['Non', 'non', 'n']:
    database_created = input("Avez-vous créer les base de donnée? (cantina-administration, cantina-cloud) ")
    while database_created not in ['Oui', 'oui', 'o', 'Non', 'non', 'n']:
        print("Les réponses valides sont: 'Oui', 'oui', 'o' ou 'Non', 'non', 'n'")
        database_created = input("Avez-vous créer les base de donnée? (cantina-administration, cantina-cloud) ")

    if database_created in ['Non', 'non', 'n']:
        exit("Merci de créer les bases de données!")
    elif database_created in ['Oui', 'oui', 'o']:
        pass

    print("Identifiants de connexion aux bases de données: ")
    database_username = input("    Nom d'utilisateur: ")
    database_password = input("    Mots de passe: ")

    while database_password == '' or database_username == '':
        print("Merci de rentrer des valeurs!")
        database_username = input("    Nom d'utilisateur: ")
        database_password = input("    Mots de passe: ")

    try:
        con = connect(user=database_username, password=database_password, host="localhost", port=3306)
        cursor = con.cursor()

    except Exception as e:
        exit("Un problème est apparue lors de la connexion à Mariadb: " + str(e))

    cursor.execute("""SHOW DATABASES""")
    data = cursor.fetchall()

    for i in data:
        if i[0] == 'cantina_administration':
            database[0] = True
        elif i[0] == 'cantina_cloud':
            database[1] = True

    if not database[0] or not database[1]:
        exit("Merci de créer les bases de données!\n cantina_administration: " + str(database[0]) +
             "\ncantina_cloud: " + str(database[1]))

    cursor.execute("USE cantina_administration")

    cursor.execute("CREATE TABLE IF NOT EXISTS user(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT,  "
                   "user_name TEXT, salt TEXT, password TEXT, admin BOOL, work_Dir TEXT, last_online TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS log(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, name TEXT,  "
                   "user_ip text, user_token TEXT, argument TEXT, log_level INT, date TIMESTAMP NOT NULL "
                   "DEFAULT CURRENT_TIMESTAMP)")

    print("Nous allons donc créer un premier compte administrateur.")
    username = input("    Nom d'utilisateur: ")
    mdp = input("    Mots de passe: ")

    salt = sha256().hexdigest()
    cursor.execute(f"""INSERT INTO user(token, user_name, salt, password, admin, work_Dir) VALUES (%s, %s, %s, %s, %s, 
    %s) """, (str(uuid3(uuid1(), str(uuid1()))), username, salt,
              salt_password(mdp, salt, new_account=True), 1, '/home/cantina/cloud/file_cloud/' + username))

    cursor.execute("USE cantina_cloud")
    cursor.execute("CREATE TABLE IF NOT EXISTS file_sharing(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, file_name TEXT,"
                   " file_owner text, file_short_name TEXT, login_to_show BOOL DEFAULT 1, password TEXT,"
                   "date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS api(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, "
                   "api_name TEXT, api_desc TEXT, owner TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS api_permission(token_api TEXT, create_file BOOL, upload_file BOOL, "
                   "delete_file BOOL, create_folder BOOL, delete_folder BOOL, share_file_and_folder BOOL, "
                   "delete_share_file_and_folder BOOL, create_user BOOL, delete_user BOOL)")

print(CRED +
      "----------------------------------------------------------------------------------------------------------------"
      "--------------------------------------------------------" + CEND
      )

con.commit()


json_data = {
  "database": [{
    "database_username": database_username,
    "database_password": database_password,
    "database_administration_name": "cantina_administration",
    "database_cloud_name": "cantina_cloud"
  }],
  "port": 2001
}

with open("/home/cantina/cloud/config.json", "w") as outfile:
    outfile.write(dumps(json_data, indent=4))

launch_startup = input("Voullez vous lancez Cantina Cloud au lancement de votre serveur? ")
system("touch /etc/systemd/system/cloud.service")
system(f"""echo '[Unit]
Description=Cantina Cloud
[Service]
User=cantina
WorkingDirectory=/home/cantina/cloud
ExecStart=python3 app.py
[Install]
WantedBy=multi-user.target' >> /etc/systemd/system/cantina-cloud.service""")
system('chown cantina:cantina /home/cantina/*/*/*')
system("systemctl enable cantina-cloud")
system("systemctl start cantina-cloud")
print(CRED +
      "----------------------------------------------------------------------------------------------------------------"
      "--------------------------------------------------------" + CEND
      )
system("rm -r /home/cantina/cloud/installation")
print("Nous venons de finir l'instalation de Cantina! Vous pouvez maintenant configurer votre serveur web pour qu'il "
      "pointe sur l'ip 127.0.0.1:2001!")

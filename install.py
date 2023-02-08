import json
import os
import hashlib
import uuid
import argon2
import mariadb
import platform


mdp2 = ""
username = None
mdp = None
conf1 = False
already_an_instance = [False, False]
data_id = False
os_info = platform.uname()


def salt_password(passwordtohash, user_name, new_account=False):
    try:
        if not new_account:
            pass
        else:
            passw = hashlib.sha256(argon2.argon2_hash(passwordtohash, user_name)).hexdigest().encode()
            return passw

    except AttributeError as e:
        print(e)
        return None


if os.geteuid() != 0:
    exit("L'installation doit être fait en root!")
if os_info[0] != "Linux":
    exit("L'installation doit être faite sur un système Linux!")
print("Bienvenue dans l'installation de Cantina Cloud!")
if "Debian" in os_info.version:
    os.system("sudo adduser cantina --system")
    os.system("sudo addgroup cantina")
else:
    os.system("sudo useradd cantina")
    os.system("sudo groupadd cantina")
os.system("sudo usermod -a -G cantina cantina")
os.system("git clone https://github.com/Cantina-Org/Cloud /home/cantina/cloud")
os.system("mkdir /home/cantina/cloud/file_cloud /home/cantina/cloud/share")
os.system("pip install Flask")

print("---------------------------------------------------------------------------------------------------------------")
while not conf1:
    print("Configuration de la base de donnée:")
    db_uname = input("  Nom d'utilisateur de la base de donnée: ")
    db_passw = input("  Mot de passe de la base de donnée: ")
    try:
        con = mariadb.connect(user=db_uname, password=db_passw, host="localhost", port=3306)
        cursor = con.cursor()
        cursor.execute("""SHOW DATABASES""")
        data = cursor.fetchall()

        for i in data:
            if i[0] == 'cantina_administration':
                already_an_instance[0] = True
            elif i[0] == 'cantina_cloud':
                already_an_instance[1] = True
    except Exception as e:
        print(e)
        exit("Identifiants incorrect!")
    if not already_an_instance[0] or not already_an_instance[1]:
        exit("Merci de créer les bases de données pour pouvoir continuer!")
    cursor.execute("USE cantina_administration")
    try:
        cursor.execute("SELECT id, user_name FROM user")
        data_id = cursor.fetchall()
        if already_an_instance[0] and len(data_id) >= 1:
            data_id = True
            print("Une instance de Cantina à déjà été crée. Pour vous connectez à Cantina Cloud, utiliser les mêmes "
                  "utilisateur.")
        else:
            raise "No user found in database"
    except Exception as e:
        print(e)
        print("Nous allons donc créer un premier compte administrateur.")
        username = input("  Nom d'utilisateur: ")
        mdp = input("  Mot de passe: ")
    print("Configuration de Cantina")
    port = input("  Port de Cantina: ")
    confirm = input("Confirmez vous les données ci-dessus? ")

    if confirm == "yes" or confirm == "oui" or confirm == "y" or confirm == "o":
        if not username or not mdp or not db_uname or not db_passw or not port:
            if not username or not mdp and already_an_instance:
                conf1 = True
            else:
                conf1 = False
        else:
            conf1 = True

print("---------------------------------------------------------------------------------------------------------------")

if already_an_instance[0] and already_an_instance[1]:
    cursor.execute("USE cantina_administration")

    cursor.execute("CREATE TABLE IF NOT EXISTS user(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, "
                   "user_name TEXT, password TEXT, admin BOOL, work_Dir TEXT, online BOOL, last_online TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS log(id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, name TEXT, user_ip text,"
                   "user_token TEXT, argument TEXT, log_level INT, date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    if not data_id:
        salt = hashlib.sha256().hexdigest()
        cursor.execute(f"""INSERT INTO user(token, user_name, salt, password, admin, work_Dir) VALUES (?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid3(uuid.uuid1(), str(uuid.uuid1()))), username, salt,
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

con.commit()
for i in data_id:
    os.system("mkdir /home/cantina/cloud/file_cloud/{} /home/cantina/cloud/share/{}".format(i[1], i[1]))

json_data = {
  "database": [{
    "database_username": db_uname,
    "database_password": db_passw,
    "database_administration_name": "cantina_administration",
    "database_cloud_name": "cantina_cloud"
  }],
  "port": port
}
with open("/home/cantina/cloud/config.json", "w") as outfile:
    outfile.write(json.dumps(json_data, indent=4))

launch_startup = input("Voullez vous lancez Cantina Cloud au lancement de votre serveur?")
os.system("touch /etc/systemd/system/cloud.service")
os.system(f"""echo '[Unit]
Description=Cantina Cloud
[Service]
User=cantina
WorkingDirectory=/home/cantina/cloud
ExecStart=python3 app.py
[Install]
WantedBy=multi-user.target' >> /etc/systemd/system/cantina-cloud.service""")
os.system('chown cantina-cloud /home/cantina/*/*/* && chgrp cantina-cloud /home/cantina/*/*/*')
os.system("systemctl enable cantina-cloud")
os.system("systemctl start cantina-cloud")

print("---------------------------------------------------------------------------------------------------------------")
os.system("rm /home/cantina/cloud/install.py")
print("Nous venons de finir l'instalation de Cantina! Vous pouvez maintenant configurer votre serveur web pour qu'il "
      "pointe sur l'ip 127.0.0.1:{}!".format(port))

import json
import os
import hashlib
import uuid
import mariadb

mdp = ""
mdp2 = ""
conf1 = False


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


if os.geteuid() != 0:
    exit("L'installation doit être fait en root!")

print("Bienvenue dans l'installation de Cantina Cloud!")
os.system("sudo adduser cantina --system")
os.system("sudo addgroup cantina")
os.system("git clone https://github.com/Cantina-Org/cantina.git /home/cantina/cloud")
os.system("mkdir /home/cantina/cloud/file_cloud /home/cantina/cloud/share")
os.system("pip install Flask")

print("---------------------------------------------------------------------------------------------------------------")
while not conf1:
    print("Nous allons donc créer un premier compte administrateur.")
    username = input("  Nom d'utilisateur: ")
    mdp = input("  Mot de passe: ")

    print("Configuration de la base de donnée:")
    db_name = input("  Nom de la base de donnée: ")
    db_passw = input("  Mot de passe de la base de donnée: ")
    db_uname = input("  Nom d'utilisateur de la base de donnée: ")
    confirm = input("Confirmez vous les données ci-dessus? ")
    if confirm == "yes" or confirm == "oui" or confirm == "y" or confirm == "o":
        if not username or not mdp or not db_uname or not db_name or not db_passw:
            conf1 = False
        else:
            conf1 = True

print("---------------------------------------------------------------------------------------------------------------")

con = mariadb.connect(user=db_uname, password=db_passw, host="localhost", port=3306, database=db_name)
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
cursor.execute(f'''INSERT INTO user(token, user_name, password, admin, work_Dir) VALUES (?, ?, ?, ?, ?)''', (
    str(uuid.uuid3(uuid.uuid1(), str(uuid.uuid1()))), username, hash_perso(mdp), 1,
    '/home/cantina/cloud/file_cloud/' + username))
con.commit()
os.system("mkdir /home/cantina/cloud/file_cloud/matbe /home/cantina/cloud/share/matbe")

json_data = {"database_username": db_uname, "database_password": db_passw, "database_name": db_name}
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
WantedBy=multi-user.target' >> /etc/systemd/system/cantina.service""")
os.system('chown cantina /home/cantina/*/*/* && chgrp cantina /home/cantina/*/*/*')
os.system("systemctl enable cantina")
os.system("systemctl start cantina")

print("---------------------------------------------------------------------------------------------------------------")
os.system("rm /home/cantina/cloud/installer.py")
print("Nous venons de finir l'instalation de Cantina! Vous pouvez maintenant sur https://127.0.0.1:5000/  pour pouvoir "
      "continuer l'installation de Cantina")

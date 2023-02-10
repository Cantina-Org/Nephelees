import os
import platform

CRED = '\033[91m'
CEND = '\033[0m'
based_on = None
os_info = platform.uname()

if os.getuid() != 0:
    exit("L'installation doit être faite avec les permissions d'administrateur!")
elif os_info.system != "Linux":
    exit("L'installation doit être faire sur une système linux!")

print("Bienvenue dans l'installation de Cantina Cloud!")

if "Debian" in os_info.version:
    print("Système Debian détecter.")
    os.system("sudo adduser cantina --system")
    os.system("sudo addgroup cantina")
else:
    distrib_check = input(
        "Votre système est:\n     1: Basé sur Debian\n     2: Basé sur Arch\n     3: Basé sur Red Hat")
    while distrib_check not in ["1", "2", "3"]:
        print("Merci de répondre uniquement par 1, 2 ou 3!")
        distrib_check = input(
            "Votre système est:\n     1: Basé sur Debian\n     2: Basé sur Arch\n     3: Basé sur Red Hat")

    if distrib_check == "1" or distrib_check == "3":
        os.system("sudo adduser cantina --system")
        os.system("sudo addgroup cantina")
    elif distrib_check == "2":
        os.system("sudo useradd cantina")
        os.system("sudo groupadd cantina")
    else:
        exit("Vous avez cassé notre système :/")

os.system("sudo usermod -a -G cantina cantina")
os.system("git clone https://github.com/Cantina-Org/Cloud /home/cantina/cloud")
os.system("mkdir /home/cantina/cloud/file_cloud /home/cantina/cloud/share")
os.system("pip install Flask")

print(CRED +
      "----------------------------------------------------------------------------------------------------------------"
      "------" + CEND
      )

new_instance = input("Avez vous déjà installé sur ce serveur une projet Cantina?")
while new_instance not in ['Oui', 'oui', 'o', 'Non', 'non', 'n']:
    print("Les réponses valides sont: 'Oui', 'oui', 'o' ou 'Non', 'non', 'n'")
    new_instance = input("Avez vous déjà installé sur ce serveur une projet Cantina?")

if new_instance in ['Non', 'non', 'n']:
    print("Déjà des trucs")
elif new_instance in ['Oui', 'oui', 'o']:
    print("Un nouveau départ")

print(CRED +
      "----------------------------------------------------------------------------------------------------------------"
      "------" + CEND
      )


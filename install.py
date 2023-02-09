import os
import platform

based_on = None
os_info = platform.uname()

if os.getuid() != 0:
    exit("L'installation doit être faite avec les permissions d'administrateur!")
elif os_info.system != "Linux":
    exit("L'installation doit être faire sur une système linux!")

print("Bienvenue dans l'installation de Cantina Cloud!")

if "Debian" in os_info.version:
    print("Système Debian détecter.")
    based_on = "Debian"
else:
    distrib_check = input(
        "Votre système est:\n     1: Basé sur Debian\n     2: Basé sur Arch\n     3: Basé sur Red Hat")
    while distrib_check not in ["1", "2", "3"]:
        print("Merci de répondre uniquement par 1, 2 ou 3!")
        distrib_check = input(
            "Votre système est:\n     1: Basé sur Debian\n     2: Basé sur Arch\n     3: Basé sur Red Hat")

    if distrib_check == "1": based_on = "Debian"
    elif distrib_check == "2": based_on = "Arch"
    elif distrib_check == "3": based_on = "Red Hat"
    else: exit("Vous avez cassé notre système :/")


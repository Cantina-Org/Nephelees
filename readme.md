# Néphélées

Néphélées est le SSO (Single Sign On) de la suite cantina

### ⚠️: Installer Néphélées peut causer des problèmes sur votre machine si vous faites de mauvaises manipulations ! À vos risques et périls 😆 !

***

## Contribuer :

#### Attention : l'installation de l'outil [Néphélées](https://github.com/Cantina-Org/Néphélées) (conseillé via [Ouranos](https://github.com/Cantina-Org/Ouranos)) est obligatoire ! (Sinon c'est un peu comme avoir une voiture sans les roues 😇.)

### Étape 1:
Cloner votre [fork](https://github.com/Cantina-Org/Néphélées/fork) de Néphélées.

### Étapes 2:
Créer un fichier `config.json` à la racine du projet Néphélées.

### Étapes 3:
Remplisser le fichier `config.json` avec ça: 
```json
{
    "database": [
        {
            "database_username": "",
            "database_password": "",
            "database_addresse": "",
            "database_port": ""
        }
    ],
    "port": 3000
}
``` 
Compléter les champs de la catégorie `database` avec les identifiants de votre base de données.

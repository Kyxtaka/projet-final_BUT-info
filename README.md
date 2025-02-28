# projet-finale_BUT-info
Groupe : Akhtar Naima, Bocquet Clemence, Randrianstoa Nathan, Valin Ophelie, Vilcoq Yohann

## Table des matières 
- Introduction
  * Le sujet
  * L'application
- Lancement application

## Introduction
> Différents types d’intempéries laissent des dégâts irréversibles sur des biens matériels d’un logement. Ces dommages sont souvent garantis par une assurance habitation.  
>  Toutefois, pour faire constater les dégâts d’événements météorologiques, il est nécessaire de réaliser une démarche auprès de l’assureur listant l’ensemble des dommages subis et des justificatifs d’achat associés.

> MobiList est une application de gestion de biens matériels d’un logement. Celle-ci va permettre d’informatiser ce processus en dressant un inventaire des biens par pièces, de conserver les preuves d’achats et de calculer l’usure du bien au moment du dommage.
> Ainsi, lors de dégâts subis, l’application permettra de fournir un état financier des possibles pertes en fonction de leur vétusté et d’afficher les justificatifs d’achats associés.

Pour vous accompagner dans l'utilisation de Mobilist, vous trouverez dans le dossier 'Manuels' le manuel d'installation et le manuel utilisateur.

## Lancement application
### Installation
Pour vous aider dans l'installation du projet, vous pouvez vous référer au manuel d'installation.  
Vous devez avoir préalablement créer un environnement virtuel, télécharger le projet et installer les dépendances.
### Lancer l'application
> Vous pouvez lancer l'application avec **flask run**  
> Ouvrir la page depuis le lien donné (Running on http://127.0...)

Vous pouvez vous référer au manuel d'utilisation.

### Lancer les tests
Pour lancer les tests, à la racine du projet ```python -m pytest``` ou  ```coverage run -m pytest```  
Pour obtenir la couverture, à la racine du projet ```coverage html --omit=mobilist/commands.py,mobilist/routes/PDF/generatePDF.py```


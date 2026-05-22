# Bot Discord Strapontia

## Installation

1. Installe Python 3.10+ depuis https://python.org
   ⚠️ Coche "Add Python to PATH" pendant l'installation !

2. Ouvre un terminal dans ce dossier et installe les dépendances :
   pip install -r requirements.txt

3. Ouvre bot.py et remplace :
   TOKEN = "METS_TON_TOKEN_ICI"
   par ton vrai token Discord

4. Lance le bot :
   python bot.py

## Commandes Discord

!status   → Affiche le statut du serveur
!joueurs  → Affiche la liste des joueurs connectés

## Statut automatique

Le bot met à jour automatiquement un message dans le channel
toutes les 60 secondes avec le nombre de joueurs en ligne.

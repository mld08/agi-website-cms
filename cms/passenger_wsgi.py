"""Point d'entrée WSGI pour cPanel (« Setup Python App » utilise Passenger).

Dans cPanel, l'application Python pointe vers ce dossier ; Passenger importe la
variable « application » ci-dessous. Après chaque déploiement ou changement de
code, cliquez sur « Restart » dans l'interface « Setup Python App ».
"""
from app import app as application

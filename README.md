# TP Ethical Hacking - Client/Serveur Python

## Architecture
- `src/c2/` : Serveur C2 (Kali)
- `src/win/` : Client Windows
- `src/lin/` : Client Linux
- `bin/` : Lanceurs (sh / bat)

## Fonctionnalités Client
- Connexion Socket TCP (JSON)
- Exécution de commandes (Shell/PowerShell)
- Capture d'écran
- Persistance (Crontab/Registre)
- Énumération (SAM/Regedit, passwd/shadow, root/home)
- Gestion d'erreurs et reconnexion automatique
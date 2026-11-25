
import getpass
import platform
import socket
import os
import stat


def get_system_info():
    """Récupère les informations générales du système Linux."""

    return {
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "system": platform.system(),
        "distribution": platform.platform(),
        "architecture": platform.machine()
    }


def get_users_info():
    """Récupère les métadonnées des comptes depuis /etc/passwd."""

    users = []

    try:
        with open("/etc/passwd", "r", encoding="utf-8") as file:
            for line in file:
                fields = line.strip().split(":")

                if len(fields) != 7:
                    continue

                users.append({
                    "username": fields[0],
                    "uid": fields[2],
                    "gid": fields[3],
                    "home": fields[5],
                    "shell": fields[6]
                })

    except OSError as error:
        print(f"[-] Erreur de lecture : {error}")

    return users


def list_directory(path, max_entries=5):
    """Affiche un échantillon des éléments accessibles."""

    print(f"\n[+] Exploration : {path}")

    count = 0

    try:
        for root, directories, files in os.walk(
            path,
            onerror=lambda error: None,
            followlinks=False
        ):
            for name in directories + files:

                if count >= max_entries:
                    print("[+] Affichage limité.")
                    return

                full_path = os.path.join(root, name)

                try:
                    information = os.lstat(full_path)
                    permissions = stat.filemode(information.st_mode)

                    if stat.S_ISDIR(information.st_mode):
                        file_type = "Dossier"
                    elif stat.S_ISREG(information.st_mode):
                        file_type = "Fichier"
                    elif stat.S_ISLNK(information.st_mode):
                        file_type = "Lien"
                    else:
                        file_type = "Autre"

                    print(f"{file_type} | {permissions} | {name}")
                    count += 1

                except OSError:
                    continue

        print(f"[+] {count} élément(s) affiché(s)")

    except OSError:
        print("[-] Accès impossible.")


if __name__ == "__main__":

    print("[+] INFORMATIONS SYSTÈME")

    information = get_system_info()

    for key, value in information.items():
        print(f"{key} : {value}")

    print("\n[+] COMPTES UTILISATEURS")

    users = get_users_info()

    print(f"Nombre de comptes : {len(users)}")

    for user in users:
        print(
            f"{user['username']} | "
            f"UID: {user['uid']} | "
            f"GID: {user['gid']}"
        )

    print("\n[+] EXPLORATION DES RÉPERTOIRES")

    list_directory("/home", max_entries=5)
    list_directory("/root", max_entries=5)

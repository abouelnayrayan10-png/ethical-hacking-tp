import os
import stat
import getpass
import platform
import socket

def list_directory(path):
    """Liste récursivement les éléments accessibles d'un dossier."""

    print(f"\n[+] Exploration de : {path}")

    try:
        for root, directories, files in os.walk(
            path,
            onerror=lambda error: print(
                f"[-] Accès refusé : {error.filename}"
            ),
            followlinks=False
        ):
            for name in directories + files:
                full_path = os.path.join(root, name)

                try:
                    information = os.lstat(full_path)

                    if stat.S_ISLNK(information.st_mode):
                        file_type = "Lien symbolique"
                    elif stat.S_ISDIR(information.st_mode):
                        file_type = "Dossier"
                    elif stat.S_ISREG(information.st_mode):
                        file_type = "Fichier"
                    else:
                        file_type = "Autre"

                    permissions = stat.filemode(information.st_mode)

                    print(
                        f"{file_type} | "
                        f"{permissions} | "
                        f"{full_path}"
                    )

                except OSError as error:
                    print(f"[-] Impossible d'accéder à {full_path} : {error}")

    except OSError as error:
        print(f"[-] Erreur d'exploration : {error}")
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
        print(f"[-] Erreur de lecture de /etc/passwd : {error}")

    return users


if __name__ == "__main__":
    information = get_system_info()

    print("[+] Informations système :")

    for key, value in information.items():
        print(f"{key} : {value}")

    print("\n[+] Comptes utilisateurs Linux :")

    users = get_users_info()

    for user in users:
        print(
            f"Utilisateur : {user['username']} | "
            f"UID : {user['uid']} | "
            f"GID : {user['gid']} | "
            f"Home : {user['home']} | "
            f"Shell : {user['shell']}"
        )

        print("\n[+] Exploration des répertoires Linux :")

    list_directory("/home")
    list_directory("/root")

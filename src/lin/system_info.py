
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


def list_directory(path, max_scan=500, max_display=5):
    """Explore récursivement un dossier sans lire les fichiers."""

    print(f"\n[+] Exploration récursive : {path}")

    count_files = 0
    count_directories = 0
    samples = []
    scan_limit_reached = False

    def handle_error(error):
        print(f"[-] Accès refusé : {error.filename}")

    try:
        for root, directories, files in os.walk(
            path,
            onerror=handle_error,
            followlinks=False
        ):
            for name in directories + files:

                if count_files + count_directories >= max_scan:
                    scan_limit_reached = True
                    break

                full_path = os.path.join(root, name)

                try:
                    information = os.lstat(full_path)
                    permissions = stat.filemode(information.st_mode)

                    if stat.S_ISDIR(information.st_mode):
                        file_type = "Dossier"
                        count_directories += 1

                    elif stat.S_ISREG(information.st_mode):
                        file_type = "Fichier"
                        count_files += 1

                    elif stat.S_ISLNK(information.st_mode):
                        file_type = "Lien"

                    else:
                        file_type = "Autre"

                    if len(samples) < max_display:
                        samples.append(
                            f"{file_type} | {permissions} | {full_path}"
                        )

                except OSError:
                    continue

            if scan_limit_reached:
                break

        for sample in samples:
            print(sample)

        if scan_limit_reached:
            print("[!] Limite de sécurité du parcours atteinte.")

        print(f"[+] Dossiers trouvés : {count_directories}")
        print(f"[+] Fichiers trouvés : {count_files}")
        print(f"[+] Éléments affichés : {len(samples)}")

    except OSError as error:
        print(f"[-] Erreur d'exploration : {error}")


if __name__ == "__main__":

    print("[+] INFORMATIONS SYSTÈME")

    information = get_system_info()

    for key, value in information.items():
        print(f"{key} : {value}")

    print("\n[+] COMPTES UTILISATEURS")

    users = get_users_info()

    print(f"Nombre total de comptes : {len(users)}")

    for user in users:
        if user["username"] == getpass.getuser():
            print(
                f"Utilisateur principal : {user['username']} | "
                f"UID : {user['uid']} | "
                f"GID : {user['gid']}"
            )

    print("\n[+] EXPLORATION DES RÉPERTOIRES")

    list_directory("/home")
    list_directory("/root")

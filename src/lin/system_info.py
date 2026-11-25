
import getpass
import platform
import socket


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

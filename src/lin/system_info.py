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


if __name__ == "__main__":
    information = get_system_info()

    print("[+] Informations système :")

    for key, value in information.items():
        print(f"{key} : {value}")
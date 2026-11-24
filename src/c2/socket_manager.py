
import socket

from protocol import encode_message, decode_message


class SocketManager:
    """Gestion des connexions TCP du serveur."""

    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.server_socket = None

    def start(self):
        """Démarre le serveur TCP."""
        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"[+] Serveur en écoute sur {self.host}:{self.port}")

    def accept_client(self):
        """Accepte une connexion entrante."""
        client_socket, address = self.server_socket.accept()

        print(f"[+] Connexion reçue de {address}")

        return client_socket, address

    def close(self):
        """Ferme proprement le serveur."""
        if self.server_socket:
            self.server_socket.close()
            print("[+] Serveur arrêté")

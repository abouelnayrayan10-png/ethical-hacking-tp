
import threading

from .socket_manager import SocketManager
from .protocol import encode_message, decode_message
from .error_handler import handle_error


def handle_client(client_socket, address):
    """Gère individuellement une connexion cliente."""

    print(f"[+] Traitement du client {address}")

    try:
        with client_socket:
            with client_socket.makefile("rb") as client_file:
                data = client_file.readline()

            if not data:
                print(f"[-] Client {address} déconnecté.")
                return

            message = decode_message(data)
            print(f"[+] Message reçu de {address} : {message}")

            response = {
                "type": "response",
                "message": "Connexion au serveur réussie !"
            }

            client_socket.sendall(encode_message(response))

    except (OSError, ValueError) as error:
        handle_error(error, f"client {address}")



def main():
    """Démarre le serveur et accepte plusieurs clients."""

    server = SocketManager(host="0.0.0.0", port=5000)

    try:
        server.start()

        while True:
            client_socket, address = server.accept_client()

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True
            )

            client_thread.start()

    except KeyboardInterrupt:
        print("\n[!] Arrêt demandé par l'utilisateur.")

    except OSError as error:
        handle_error(error, "serveur")

    finally:
        server.close()


if __name__ == "__main__":
    main()

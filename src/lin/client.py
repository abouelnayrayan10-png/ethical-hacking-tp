
import socket
import platform


def get_network_interfaces():
    """Affiche les adresses IPv4 associées à la machine."""

    print("===== INTERFACES RÉSEAU =====")

    try:
        interfaces = socket.getaddrinfo(
            socket.gethostname(),
            None,
            socket.AF_INET
        )

        addresses = sorted({
            info[4][0] for info in interfaces
            if not info[4][0].startswith("127.")
        })

        if not addresses:
            print("Aucune adresse IPv4 détectée.")
            return

        for index, address in enumerate(addresses, start=1):
            print(f"Adresse IPv4 {index} : {address}")

    except socket.gaierror as error:
        print(f"Erreur réseau : {error}")


def main():
    print("===== INFORMATIONS DE LA MACHINE =====")
    print(f"Système : {platform.system()}")
    print(f"Nom de la machine : {socket.gethostname()}")

    get_network_interfaces()


if __name__ == "__main__":
    main()

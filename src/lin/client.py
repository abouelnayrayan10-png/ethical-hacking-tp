
import socket
import platform
import psutil


def get_network_interfaces():
    print("===== INTERFACES RÉSEAU =====")

    try:
        interfaces = psutil.net_if_addrs()
        found = False

        for interface_name, addresses in interfaces.items():
            for address in addresses:
                if (
                    address.family == socket.AF_INET
                    and not address.address.startswith("127.")
                ):
                    print(f"Interface : {interface_name}")
                    print(f"Adresse IPv4 : {address.address}")
                    found = True

        if not found:
            print("Aucune adresse IPv4 détectée.")

    except psutil.Error as error:
        print(f"Erreur lors de la détection réseau : {error}")
    except OSError as error:
        print(f"Erreur système : {error}")


def main():
    try:
        print("===== INFORMATIONS DE LA MACHINE =====")
        print(f"Système : {platform.system()}")
        print(f"Nom de la machine : {socket.gethostname()}")
        get_network_interfaces()

    except Exception as error:
        print(f"Erreur inattendue : {error}")


if __name__ == "__main__":
    main()

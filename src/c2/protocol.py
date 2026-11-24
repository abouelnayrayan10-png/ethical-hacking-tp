import json


def encode_message(data: dict) -> bytes:
    """Convertit un dictionnaire en message JSON."""
    message = json.dumps(data)
    return (message + "\n").encode("utf-8")


def decode_message(data: bytes) -> dict:
    """Convertit un message JSON en dictionnaire."""
    message = data.decode("utf-8").strip()
    result = json.loads(message)

    if not isinstance(result, dict):
        raise ValueError("Le message doit être un objet JSON.")

    return result

from datetime import datetime


def handle_error(error, context=""):
    """Affiche une erreur avec son contexte et son horodatage."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(
        f"[-] [{timestamp}] "
        f"Erreur {context} : {type(error).__name__} - {error}"
    )

import os
from pathlib import Path

AXIE_MARKETPLACE_BASE = os.environ.get("AXIE_MARKETPLACE_BASE", "https://app.axieinfinity.com/")
AXIE_MARKETPLACE_PROFILE = AXIE_MARKETPLACE_BASE + "profile/"
AXIE_MARKETPLACE_AXIEVIEW = AXIE_MARKETPLACE_BASE + "marketplace/axies/"


# --- CARGAR VARIABLES DE ENTORNO ---
def load_env():
    # Buscar .env en la raíz del proyecto (un nivel arriba de core/)
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Limpiar comillas si existen
                    value = value.strip("'").strip('"')
                    os.environ[key] = value


def update_env_var(key, new_value):
    """Actualiza o añade una variable en el archivo .env y en os.environ."""
    env_path = Path(__file__).parent.parent / ".env"
    lines = []
    found = False

    # Leer contenido existente si el archivo existe
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # Modificar o añadir linea
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={new_value}\n"
            found = True
            break

    if not found:
        # Añadir al final, asegurando que haya un salto de linea antes si el archivo no termina en uno
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
        lines.append(f"{key}={new_value}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    os.environ[key] = str(new_value)


def format_ronin_address(address):
    """Convierte una dirección 0x... a ronin:0x..."""
    if not address:
        return ""
    if address.startswith("ronin:"):
        return address
    if address.startswith("0x"):
        return f"ronin:{address[2:]}"
    return address


def format_currency(amount):
    """Formatea un valor monetario con separadores de miles y 2 decimales."""
    try:
        val = float(amount)
        return f"${val:,.2f} USD"
    except (ValueError, TypeError):
        return "$0.00 USD"


def get_axie_url(axie_id):
    """Genera la URL del marketplace para un Axie."""
    return f"{AXIE_MARKETPLACE_AXIEVIEW}{axie_id}/"


def get_wallet_url(address):
    """Genera la URL del marketplace para una billetera."""
    return f"{AXIE_MARKETPLACE_PROFILE}{address}/axie/"

import os
from pathlib import Path


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
    return f"https://app.axieinfinity.com/marketplace/axies/{axie_id}/"


def get_wallet_url(address):
    """Genera la URL del marketplace para una billetera."""
    return f"https://app.axieinfinity.com/profile/{address}/axie/"

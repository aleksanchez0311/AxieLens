import sys
import json
import logging
from pathlib import Path

# Añadir el directorio raíz al path para poder importar los módulos core
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from core.moralis import Moraliscore
from core.skymavis import SkyMaviscore
from core.utils import load_env

# Cargar variables de entorno
load_env()


class AxieLogic:
    def __init__(self):
        self.moralis = Moraliscore()
        self.skymavis = SkyMaviscore()
        self.owners_data = self.load_owners_data()

    def load_owners_data(self):
        """Carga el mapeo de nombres y billeteras desde el archivo JSON."""
        try:
            # Intentar en el directorio actual o en la raíz
            data_path = root_dir / "wallets_for_first_owner_finding.json"
            if data_path.exists():
                with open(data_path, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error cargando wallets_for_first_owner_finding.json: {e}")
            return {}

    def get_owner_name(self, address):
        """Normaliza y busca si la dirección pertenece a la lista de dueños."""
        if not address or address == "0x0000000000000000000000000000000000000000":
            return None
        search_addr = address.lower().replace("ronin:", "0x")
        for owner_name, wallets in self.owners_data.items():
            if isinstance(wallets, dict):
                for wallet_addr in wallets.values():
                    if wallet_addr.lower().replace("ronin:", "0x") == search_addr:
                        return owner_name
        return None

    def get_first_owner(self, axie_id):
        """Rastrea el historial para encontrar el primer dueño (priorizando match en lista)."""
        try:
            res = self.moralis.get_nft_transfers(axie_id)
            if not res or "result" not in res or not res["result"]:
                return None

            history = list(reversed(res["result"]))

            # 1. Buscar match en nuestra lista
            for tx in history:
                to_addr = tx.get("to_address")
                if self.get_owner_name(to_addr):
                    return to_addr

            # 2. Fallback al primer poseedor real (que no sea el address 0)
            first = history[0]
            if first.get("from_address").startswith("0x000"):
                return first.get("to_address")
            return first.get("from_address")
        except Exception as e:
            logging.error(f"Error en lógica de primer dueño para #{axie_id}: {e}")
            return None

    def get_complete_axie_data(self, axie_id):
        """Obtiene toda la información de un Axie incluyendo valoración y primer dueño."""
        data = self.moralis.get_axie_by_id(axie_id)
        if data:
            data["id"] = axie_id
            data["first_owner"] = self.get_first_owner(axie_id)
            data["valuation"] = self.skymavis.get_axie_valuation(data)
            return data
        return None

    def get_all_axies_from_wallet(self, address, adults_only=True):
        """Obtiene la lista de Axies de una billetera, filtrando solo adultos por defecto."""
        axies_raw = self.moralis.get_wallet_axies(address)
        if adults_only:
            axies = [a for a in axies_raw if a.get("stage", 4) == 4]
            return axies
        return axies_raw

    def calculate_wallet_summary(self, address):
        """Calcula el resumen económico de una billetera."""
        axies = self.get_all_axies_from_wallet(address)
        total_usd = 0
        for a in axies:
            val_data = self.skymavis.get_axie_valuation(a)
            total_usd += val_data.get("valuation_usd", 0) if val_data else 0

        return {
            "owner_name": self.get_owner_name(address),
            "total_axies": len(axies),
            "total_valuation_usd": total_usd,
            "axies": axies,
        }

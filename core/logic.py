import sys
import json
import logging
from pathlib import Path

# Añadir el directorio raíz al path para poder importar los módulos core
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from core.endpoint import get_axie_details, get_wallet_axies, get_similar_axies, get_axie_valuation

from core.utils import load_env

# Cargar variables de entorno
load_env()


class AxieLogic:
    def __init__(self):
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

    def update_owners_data(self, json_content):
        """Actualiza el archivo JSON y recarga en memoria. Retorna (True, None) o (False, error)."""
        try:
            parsed_data = json.loads(json_content)
            data_path = root_dir / "wallets_for_first_owner_finding.json"
            with open(data_path, "w") as f:
                json.dump(parsed_data, f, indent=2)
            self.owners_data = parsed_data
            return True, None
        except Exception as e:
            return False, str(e)

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

    def get_first_owner(self, axie_data):
        """Rastrea el historial para encontrar el primer dueño (priorizando match en lista)."""
        try:
            if not axie_data or "transferHistory" not in axie_data or not axie_data["transferHistory"]["results"]:
                #print("[DEBUG] get_first_owner: No hay historial de transferencias.")
                return None

            history = list(reversed(axie_data["transferHistory"]["results"]))
            #print(f"[DEBUG] get_first_owner: Historia de transferencias tiene {len(history)} entradas.")
            #print(f"[DEBUG] get_first_owner: Primera transferencia: {history[0] if history else 'None'}")

            # 1. Buscar match en nuestra lista de owners conocidos (prioriza 'to' que es el nuevo dueño)
            for tx in history:
                to_addr = tx.get("to")
                owner_name = self.get_owner_name(to_addr) if to_addr else None
                #print(f"[DEBUG] get_first_owner: Revisando 'to': {to_addr}. Owner: {owner_name}")
                if owner_name:
                    return to_addr
            
            # 2. Fallback al primer poseedor real (que no sea el address 0x0...00)
            if history:
                first_transfer_to = history[0].get("to")
                first_transfer_from = history[0].get("from")
                
                if first_transfer_from and first_transfer_from.startswith("0x000"):
                    return first_transfer_to
                else:
                    return first_transfer_from
            
            return None
        except Exception as e:
            axie_id_for_log = axie_data.get("id", "N/A") if isinstance(axie_data, dict) else "N/A"
            logging.error(f"Error en lógica de primer dueño para Axie #{axie_id_for_log}: {e}")
            return None

    def get_complete_axie_data(self, axie_id):

        """Obtiene toda la información de un Axie incluyendo valoración y primer dueño."""
        data = get_axie_details(axie_id)
        if data:
            data["first_owner"] = self.get_first_owner(data) # Pasa el axie_data completo para obtener el primer dueño
            
            # Asignar la clase y el dueño directamente desde data
            data["class_name"] = data.get("class", "N/A") # Renombrar para evitar conflicto con "class" de Python
            data["current_owner_address"] = data.get("owner", "N/A") # El campo es 'owner'
            
            similar_axies, criteria_used, total_similars = get_similar_axies(data) # Obtener axies similares
            data["valuation"] = get_axie_valuation(similar_axies) # Pasar la lista de axies similares
            
            # Almacenar información de axies similares
            data["valuation_method"] = criteria_used # El método usado para encontrar similares
            if similar_axies:
                target_valuation = data["valuation"]
                def calcular_distancia(s_axie):
                    try:
                        precio = float(s_axie.get('order', {}).get('currentPriceUsd', 0))
                        return abs(precio - target_valuation)
                    except (ValueError, TypeError):
                        return float('inf') # Distancia infinita si no hay precio válido

                # Encontramos el objeto completo que tiene la distancia mínima
                mejor_match = min(similar_axies, key=calcular_distancia)
                data["similar_axie_id"] = mejor_match.get('id')

            return data
        return None

    def get_all_axies_from_wallet(self, address, adults_only=True):
        """Obtiene la lista de Axies de una billetera, filtrando solo adultos por defecto y obteniendo su valoración."""
        import time
        start_time = time.time()
        
        # get_wallet_axies de endpoint.py ya devuelve una lista de diccionarios de Axies completos.
        axies_raw, _ = get_wallet_axies(address)
        
        print(f"[DEBUG] {len(axies_raw)} axies crudos obtenidos de la billetera en {time.time() - start_time:.2f}s")
        
        # Ahora, para cada Axie en la lista obtenida, llamamos a get_complete_axie_data
        # para que incluya la valoración.
        axies_with_valuation = []
        
        # Contador para no saturar la salida si hay muchos axies
        count = 0
        total = len(axies_raw)
        
        for axie_data in axies_raw:
            t0 = time.time()
            # Usar la versión con logs
            complete_axie_data = self.get_complete_axie_data(axie_data['id'])
            
            if complete_axie_data:
                # El filtrado por adultos se hace después de obtener los datos completos con valoración
                if adults_only and complete_axie_data.get('stage') != 4:
                    continue # Saltar si no es adulto y adults_only es True
                axies_with_valuation.append(complete_axie_data)

            count += 1
            if count % 1 == 0:
                print(f"[DEBUG] Procesando Axie {count}/{total}... ({time.time() - t0:.2f}s)")
        
        print(f"[DEBUG] Total axies procesados: {count}. Tiempo total: {time.time() - start_time:.2f}s")
        
        return axies_with_valuation

    def calculate_wallet_summary(self, address):
        """Calcula el resumen económico de una billetera."""
        axies = self.get_all_axies_from_wallet(address)
        total_usd = 0
        for a in axies:
            # get_axie_valuation ahora es una función simple que usa la data ya obtenida
            total_usd += a.get("valuation", 0)

        return {
            "owner_name": None, # No tenemos la función get_owner_name aquí
            "total_axies": len(axies),
            "total_valuation_usd": total_usd,
            "axies": axies,
        }

import requests
import os
import time


class Moraliscore:
    """Clase para manejar la conexión y solicitudes a la API de Moralis."""

    def __init__(self):
        self.key = os.environ.get("MORALIS_API_KEY", "")
        self.url = os.environ.get(
            "MORALIS_URL", "https://deep-index.moralis.io/api/v2.2"
        )
        self.contract = os.environ.get(
            "CONTRACT", "0x32953928646d7367332260ed41ce1841f3e97910"
        )  # Axie Contract
        self.chain = os.environ.get("CHAIN", "ronin")
        self.headers = {"accept": "application/json", "X-API-Key": self.key}

    def _get(self, endpoint, params=None):
        """Maneja las peticiones GET con manejo de rate limiting básico."""
        url = f"{self.url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 429:
                time.sleep(1)
                return self._get(endpoint, params)

            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[!] Error en petición Moralis ({endpoint}): {e}")
            return None

    def get_axie_by_id(self, axie_id):
        """Obtiene datos básicos de un Axie por su ID."""
        endpoint = f"/nft/{self.contract}/{axie_id}"
        params = {"chain": self.chain, "format": "decimal"}
        res = self._get(endpoint, params)
        if res:
            metadata = res.get("metadata")
            if isinstance(metadata, str):
                import json

                res["metadata"] = json.loads(metadata)
            return res
        return None

    def get_wallet_axies(self, address):
        """Obtiene todos los Axies de una billetera."""
        addr = address.lower()
        endpoint = f"/{addr}/nft"
        params = {
            "chain": self.chain,
            "format": "decimal",
            "token_addresses": [self.contract],
        }
        res = self._get(endpoint, params)
        if res and "result" in res:
            return res["result"]
        return []

    def get_nft_transfers(self, token_id):
        """
        Consulta el historial completo de transferencias de un NFT.
        Este es el método que usamos para rastrear al primer dueño.
        """
        endpoint = f"/nft/{self.contract}/{token_id}/transfers"
        params = {"chain": self.chain, "format": "decimal"}
        return self._get(endpoint, params)

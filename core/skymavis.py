import requests
import os
import re
import statistics


class SkyMaviscore:
    """
    Clase para manejar las conexiones y solicitudes a la API de Sky Mavis.
    Optimizado para evitar valuaciones infladas y generar URLs de inspección.
    """

    def __init__(self):
        # Mantiene tus variables de entorno originales
        self.marketplace = os.environ.get("AXIE_MARKETPLACE_BASE", "")
        self.key = os.environ.get("SKYMAVIS_API_KEY", "")
        self.url = os.environ.get("GRAPHQL_URL", "")
        self.bearer = os.environ.get("BEARER", "")
        self.cookie_value = os.environ.get("COOKIE_VALUE", "")

    def _execute_request(self, payload):
        """Ejecutor de peticiones con manejo de errores."""
        headers = {
            "Accept": "*/*",
            "Authorization": f"Bearer {self.bearer}",
            "Content-Type": "application/json",
            "Cookie": self.cookie_value,
            "Origin": "https://app.axieinfinity.com",
            "Referer": "https://app.axieinfinity.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "X-API-Key": self.key,
        }

        try:
            response = requests.post(
                self.url, json=payload, headers=headers, timeout=15
            )
            if response.status_code != 200:
                return None
            res_json = response.json()
            if "errors" in res_json:
                return None
            return res_json.get("data")
        except Exception:
            return None

    def fetch_marketplace(self, criteria_dict, size=10):
        """
        Busca en el mercado usando el piso de precios (PriceAsc).
        """
        query = """
        query GetAxiesMarketplace($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int) {
          axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size) {
            total
            results {
              id
              order {
                currentPriceUsd
              }
            }
          }
        }
        """
        variables = {
            "from": 0,
            "sort": "PriceAsc",
            "size": size,
            "auctionType": "Sale",
            "criteria": criteria_dict,
        }
        payload = {
            "operationName": "GetAxiesMarketplace",
            "variables": variables,
            "query": query,
        }
        data = self._execute_request(payload)
        if data and "axies" in data:
            return data["axies"]
        return None

    def search_similar_axies(self, base_axie):
        """
        Busca el Axie más similar usando el algoritmo de 9 pasos.
        Calcula la mediana y genera la URL de inspección.
        """
        if not base_axie:
            return None

        base_class = base_axie.get("class")
        body_shape = base_axie.get("bodyShape")
        parts = base_axie.get("parts", [])

        # Helpers para IDs de partes
        def get_base_id(part):
            pid = part.get("id", "")
            return re.sub(r"-\d+$", "", str(pid))

        def get_evo_id(part):
            return f"{get_base_id(part)}-2"

        # Listas de IDs para criterios
        current_ids = [str(p["id"]) for p in parts]
        base_ids = [get_base_id(p) for p in parts]

        all_parts_versions = []
        for p in parts:
            all_parts_versions.extend([get_base_id(p), get_evo_id(p)])

        # Pasos de búsqueda
        steps = [
            {
                "desc": "0. Clase + Forma + 12 partes (Evo/Base)",
                "criteria": {
                    "bodyShapes": [body_shape],
                    "classes": [base_class],
                    "parts": all_parts_versions[:12],
                },
            },
            {
                "desc": "1. Exacto (Forma/Clase/Evo)",
                "criteria": {
                    "bodyShapes": [body_shape],
                    "classes": [base_class],
                    "parts": current_ids,
                },
            },
            {
                "desc": "2. Clase + Partes (Sin Forma)",
                "criteria": {"classes": [base_class], "parts": current_ids},
            },
            {
                "desc": "5. Clase + Partes Base",
                "criteria": {"classes": [base_class], "parts": base_ids},
            },
            {"desc": "6. Solo Partes Base", "criteria": {"parts": base_ids}},
            {
                "desc": "9. Core 4 (Mouth/Horn/Back/Tail)",
                "criteria": {
                    "parts": [
                        get_base_id(p)
                        for p in parts
                        if p["type"] in ["Mouth", "Horn", "Back", "Tail"]
                    ]
                },
            },
        ]

        for step in steps:
            # Limpiar criterios
            criteria = {k: v for k, v in step["criteria"].items() if v is not None}

            # Ejecutar consulta
            data = self.fetch_marketplace(criteria, size=10)

            if data and data.get("total", 0) > 0:
                results = data["results"]
                prices = [
                    float(r["order"]["currentPriceUsd"])
                    for r in results
                    if r.get("order")
                ]

                if not prices:
                    continue

                valuation = statistics.median(prices)

                # Iterar sobre los criterios para añadir parámetros a la URL
                query_params = ""
                for key, values in criteria.items():
                    if values:
                        for val in values:
                            query_params += f"&{key}={val}"

                axie_url = f"{self.marketplace}{base_axie}"
                similars_url = f"{self.marketplace + '?auctionTypes=Sale'}{query_params}&sort=PriceAsc"
                similar_axie_url = f"{self.marketplace}{results[0]['id']}"

                # print(f"[✓] Axie: {axie_url} ==> Matched: {step['desc']} | Total en mercado: {data['total']} | Valuación: ${valuation:.2f} | Similares: {similars_url} | Axie Similar: {similar_axie_url}")

                return {
                    "axie": base_axie,
                    "valuation_usd": valuation,
                    "similar_axie_id": results[0]["id"],
                    "method": step["desc"],
                    "total_found": data["total"],
                    "similars_url": similars_url,
                    "similar_axie_url": similar_axie_url,
                }

        print("[!] No se encontraron Axies similares.")
        return None

    def get_axie_valuation(self, base_axie):
        return self.search_similar_axies(base_axie)


# ============================================
# Compatibilidad Global
# ============================================
_skymavis = SkyMaviscore()


def get_axie_valuation(base_axie):
    return _skymavis.get_axie_valuation(base_axie)

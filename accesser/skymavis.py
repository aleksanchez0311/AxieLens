import requests
import os

API_KEY = os.environ.get("SKYMAVIS_API_KEY", "")
GRAPHQL_URL = os.environ.get("GRAPHQL_URL", "")

BEARER = os.environ.get("BEARER", "")
COOKIE_VALUE = os.environ.get("COOKIE_VALUE", "")


def _execute_request(payload):
    """
    Ejecutor de peticiones con manejo de errores detallado.
    """
    headers = {
        "Accept": "*/*",
        "Authorization": f"Bearer {BEARER}",
        "Content-Type": "application/json",
        "Cookie": COOKIE_VALUE,
        "Origin": "https://app.axieinfinity.com",
        "Referer": "https://app.axieinfinity.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "X-API-Key": API_KEY,
    }

    try:
        response = requests.post(GRAPHQL_URL, json=payload, headers=headers, timeout=15)

        # Si el servidor responde pero hay algo mal
        if response.status_code != 200:
            print(f"\n[!] Error de Servidor: HTTP {response.status_code}")
            # Mostrar el contenido de la respuesta para debugging
            try:
                error_data = response.json()
                print(f"[!] Response: {error_data}")
            except:
                print(f"[!] Raw response: {response.text[:500]}")
            return None

        res_json = response.json()

        # Si la respuesta trae errores de GraphQL (permisos, tokens caducados, etc)
        if "errors" in res_json:
            error_msg = res_json["errors"][0].get("message", "Error desconocido")
            print(f"\n[!] Error GraphQL: {error_msg}")
            return None

        return res_json.get("data")

    except Exception as e:
        print(f"\n[!] Error inesperado: {e}")
        return None

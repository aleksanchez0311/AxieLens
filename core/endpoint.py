import subprocess
import json
import os
from core.utils import load_env

load_env()

SKYMAVIS_API_KEY = os.environ.get("SKYMAVIS_API_KEY")
ENDPOINT_GRAPHQL = os.environ.get("ENDPOINT_GRAPHQL", "https://api-gateway.skymavis.com/graphql/axie-marketplace")
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _run_node_script(script_path, *args):
    """Ejecuta Node.js y maneja la comunicación JSON de forma robusta."""
    env = os.environ.copy()
    if SKYMAVIS_API_KEY is None:
        print("❌ Error: SKYMAVIS_API_KEY no está configurada")
        return None
    env.update({
        "SKYMAVIS_API_KEY": SKYMAVIS_API_KEY,
        "ENDPOINT_GRAPHQL": ENDPOINT_GRAPHQL
    })
    
    cmd = ["node", script_path] + list(args)
    
    try:
        # Aumentamos el timeout a 60s por si la API de Sky Mavis está lenta
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=PROJECT_DIR, timeout=60, env=env
        )
        
        if result.returncode != 0:
            # Imprimimos el stderr para debuguear fallos de Node
            print(f"❌ Error en Node.js: {result.stderr}")
            return None
        
        return json.loads(result.stdout)
    except Exception as e:
        print(f"⚠️ Error en la ejecución: {e}")
        return None

def get_axie_details(axie_id):
    return _run_node_script(os.path.join(PROJECT_DIR, "core", "endpoint.js"), "getAxieDetails", str(axie_id))

def get_wallet_axies(wallet_id, from_idx=0, size=50):
    """Obtiene los Axies de una billetera y retorna (lista, total)."""
    result = _run_node_script(
        os.path.join(PROJECT_DIR, "core", "endpoint.js"),
        "getWalletAxies", wallet_id, str(from_idx), str(size)
    )
    
    # Ajuste: El JS devuelve un objeto con 'axies' y 'total'
    if result and isinstance(result, dict):
        return result.get('axies', []), result.get('total', 0)
    return [], 0

def get_similar_axies(axie, from_idx=0, size=10):
    """Obtiene axies similares usando la lógica recursiva del JS."""
    axie_json = json.dumps(axie)
    result = _run_node_script(
        os.path.join(PROJECT_DIR, "core", "endpoint.js"),
        "getSimilarAxies", axie_json, str(from_idx), str(size)
    )
    
    if result:
        return [result.get('axies', []), result.get('criteria', ''), int(result.get('total', 0))]
    return [[], '', 0]

def get_axie_valuation(similar_axies, tipo_calculo="median"):
    """
    Calcula el valor de mercado. 
    Tip: 'median' es generalmente lo más seguro para evitar precios inflados.
    """
    prices = [
        float(axie['order']['currentPriceUsd'])
        for axie in similar_axies
        if axie.get('order') and axie['order'].get('currentPriceUsd')
    ]
    
    if not prices: return 0.0
    
    prices.sort()
    n = len(prices)
    
    # Lógica de cálculo (Optimizada)
    if tipo_calculo == "min": return prices[0]
    if tipo_calculo == "max": return prices[-1]
    if tipo_calculo in ("avg", "average"): return sum(prices) / n
    
    if tipo_calculo == "median":
        mid = n // 2
        return (prices[mid-1] + prices[mid]) / 2 if n % 2 == 0 else prices[mid]
    
    if tipo_calculo == "floor":
        # Retorna el percentil 10 (el precio más bajo real, ignorando posibles errores)
        return prices[max(0, int(n * 0.10))]

    return prices[n // 2] # Default a median
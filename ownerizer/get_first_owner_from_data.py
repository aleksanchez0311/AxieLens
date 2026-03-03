import os
import requests
import json
import sys
import time

from finder.get_axie_details import fetch_axie_details
from comparer.get_market_comparison import get_market_comparison
from messenger.send_telegram_message import send_telegram_msg

MORALIS_API_KEY = os.environ.get("MORALIS_API_KEY", "")

AXIE_CONTRACT = os.environ.get(
    "AXIE_CONTRACT", "0x32950db2a7164ae833121501c797d79e7b79d74c"
)
MARKETPLACE_GRAPHQL = os.environ.get(
    "MARKETPLACE_GRAPHQL", "https://graphql-gateway.axieinfinity.com/graphql"
)
AXIE_MARKETPLACE_BASE = os.environ.get(
    "AXIE_MARKETPLACE_BASE", "https://app.axieinfinity.com/marketplace/axies/"
)


def normalize_address(address: str) -> str:
    if not address:
        return ""
    addr = address.strip().lower()
    if addr.startswith("ronin:"):
        addr = "0x" + addr[6:]
    return addr


def get_headers():
    return {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://app.axieinfinity.com",
        "Referer": "https://app.axieinfinity.com/",
    }


def get_valuation_by_similarity(token_id):
    """
    Usa la lógica de get_market_comparison del proyecto principal.
    """
    # Obtener detalles del axie
    axie_details = fetch_axie_details(token_id)
    if not axie_details:
        return "Error datos", ""

    # Usar get_market_comparison para obtener la valoración
    match, nivel = get_market_comparison(axie_details)

    if match:
        price_usd = match.get("order", {}).get("currentPriceUsd", "0")
        market_url = f"{AXIE_MARKETPLACE_BASE}{token_id}"
        similar_url = f"{AXIE_MARKETPLACE_BASE}?auctionTypes=Sale"
        return f"${price_usd} USD", similar_url

    return "Es mejor subastar", ""


def get_wallet_axies(wallet_address):
    addr = normalize_address(wallet_address)
    url = f"https://deep-index.moralis.io/api/v2.2/{addr}/nft?chain=ronin&token_addresses%5B0%5D={AXIE_CONTRACT}"
    headers = {"X-API-Key": MORALIS_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        return [item["token_id"] for item in res.json().get("result", [])]
    except:
        return []


def process_axie(token_id, local_db):
    # Historial de dueños vía Moralis
    url_tx = f"https://deep-index.moralis.io/api/v2.2/nft/{AXIE_CONTRACT}/{token_id}/transfers?chain=ronin&order=ASC"
    try:
        r_tx = requests.get(url_tx, headers={"X-API-Key": MORALIS_API_KEY}, timeout=10)
        txs = r_tx.json().get("result", [])
    except:
        txs = []

    owner_name, wallet_label, found = "Desconocido", "N/A", False
    for tx in txs:
        to_addr = normalize_address(tx["to_address"])
        for user, wallets in local_db.items():
            for k, v in wallets.items():
                if normalize_address(v) == to_addr:
                    owner_name, wallet_label, found = user, f"{k} ({to_addr})", True
                    break
            if found:
                break
        if found:
            break

    price, similar_url = get_valuation_by_similarity(token_id)
    market_url = f"{AXIE_MARKETPLACE_BASE}{token_id}"

    print(
        f"| ID: {token_id.ljust(10)} | Valuación: {price.ljust(15)} | Dueño: {owner_name}"
    )

    msg = (
        f"👾 *Axie #{token_id}*\n"
        f"💰 *Valuación:* {price}\n"
        f"👤 *Primer Dueño:* {owner_name}\n"
        f"👛 *Wallet:* {wallet_label}\n\n"
        f"🔗 [Ver Axie]({market_url})\n"
        f"🔍 [Ver Similares]({similar_url})"
    )
    send_telegram_msg(msg)


def main():
    print("\n--- Axie Smart Valuator (Similar Search Mode) ---")
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            local_db = json.load(f)
    except:
        print("[!] Error: data.json no encontrado.")
        return

    wallet = sys.argv[1] if len(sys.argv) > 1 else input("Wallet (0x...): ")
    axies = get_wallet_axies(wallet)

    if not axies:
        print("[!] No se encontraron Axies.")
        return

    print(f"[*] Procesando {len(axies)} Axies...\n")
    for tid in axies:
        process_axie(tid, local_db)
        time.sleep(2)


if __name__ == "__main__":
    main()

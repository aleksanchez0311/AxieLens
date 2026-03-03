import re
from pathlib import Path
import os
import sys
from finder.get_axie_details import fetch_axie_details
from comparer.get_market_comparison import get_market_comparison
from comparer.get_wallet_axies import (
    get_wallet_address_from_input,
    get_axies_for_comparison,
)

# Agregar el directorio padre al path para importar los módulos del proyecto principal
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- CONFIGURACIÓN ---
# Cargar variables de entorno desde .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key, value)


def reap_axie_id_from_url(url):
    """Extrae el ID del Axie desde una URL."""
    match = re.search(r"axies/(\d+)", url)
    return match.group(1) if match else None


def display_axie_info(axie_data, show_parts=True):
    """Muestra la información de un Axie."""
    print("=" * 60)
    print(f" DATOS DEL AXIE")
    print("=" * 60)
    print(f" ID:        {axie_data.get('id')}")
    print(f" Nombre:    {axie_data.get('name')}")
    print(f" Clase:     {axie_data.get('class')}")
    print(f" BodyShape: {axie_data.get('bodyShape')}")

    if show_parts and axie_data.get("parts"):
        print(f"\n PARTES ({len(axie_data.get('parts', []))}):")
        for part in axie_data.get("parts", []):
            stage = part.get("stage", 1)
            stage_str = " (EVO)" if stage == 2 else ""
            print(
                f"   - {part.get('type')}: {part.get('name')} ({part.get('class')}){stage_str}"
            )
    print("=" * 60)


def display_search_result(base_info, match, nivel):
    """Muestra el resultado de la búsqueda."""
    if match:
        print("=" * 60)
        print(f" RESULTADO DE LA BÚSQUEDA")
        print("=" * 60)
        print(f" Metodología: {nivel}")
        print(f" Axie Similar: #{match['id']}")
        print(f" Precio en Market: ${match['order']['currentPriceUsd']} USD")
        print(f" Enlace: https://app.axieinfinity.com/marketplace/axies/{match['id']}/")

        # Mostrar partes que quedaron
        remaining_parts = match.get("remaining_parts", [])
        if remaining_parts:
            part_map = {p["id"]: p for p in base_info.get("parts", [])}
            print(f"\n PARTES COINCIDENTES ({len(remaining_parts)}):")
            for part_id in remaining_parts:
                if part_id in part_map:
                    p = part_map[part_id]
                    stage = p.get("stage", 1)
                    stage_str = " (EVO)" if stage == 2 else ""
                    print(
                        f"   - {p.get('type')}: {p.get('name')} ({p.get('class')}){stage_str}"
                    )
                else:
                    print(f"   - {part_id}")
        print("=" * 60)
    else:
        print(
            "\n[!] No se encontraron Axies similares en venta para estimar el precio."
        )


def process_single_axie(axie_id):
    """Procesa un solo Axie desde URL del marketplace."""
    print(f"[*] Obteniendo datos del Axie #{axie_id}...")
    base_info = fetch_axie_details(axie_id)

    if not base_info:
        print("[!] Error: No se pudo obtener la información del Axie base.")
        return

    display_axie_info(base_info)
    match, nivel = get_market_comparison(base_info)
    display_search_result(base_info, match, nivel)


def process_wallet(wallet_input):
    """Procesa todos los axies de una billetera."""
    wallet_address = get_wallet_address_from_input(wallet_input)

    if not wallet_address:
        print("[!] Dirección de billetera inválida.")
        return

    print(f"[*] Obteniendo axies de la billetera: {wallet_address}...")
    axies = get_axies_for_comparison(wallet_address)

    if not axies:
        print("[!] No se encontraron axies en esta billetera.")
        return

    print(f"[*] Se encontraron {len(axies)} axies. Procesando...\n")

    results = []

    for idx, axie in enumerate(axies, 1):
        print(
            f"\n[{idx}/{len(axies)}] Procesando Axie #{axie.get('id')} - {axie.get('name')}..."
        )

        try:
            match, nivel = get_market_comparison(axie)

            if match:
                results.append(
                    {
                        "axie": axie,
                        "match": match,
                        "nivel": nivel,
                        "price": float(
                            match.get("order", {}).get("currentPriceUsd", 0)
                        ),
                    }
                )
                print(
                    f"   ✓ Encontrado: #{match['id']} - ${match['order']['currentPriceUsd']} USD"
                )
            else:
                print(f"   ✗ Sin coincidencias en marketplace")
        except Exception as e:
            print(f"   ✗ Error: {e}")

    # Mostrar resumen
    print("\n")
    print("=" * 60)
    print(" RESUMEN DE VALORACIÓN")
    print("=" * 60)
    print(f"Total de axies procesados: {len(axies)}")
    print(f"Axies con valoración encontrada: {len(results)}")
    print(f"Axies sin valoración: {len(axies) - len(results)}")

    if results:
        # Ordenar por precio
        results.sort(key=lambda x: x["price"], reverse=True)

        print("\n AXIECON VALORACIÓN (ordenados por precio):")
        for r in results:
            axie = r["axie"]
            match = r["match"]
            print(
                f"  #{axie.get('id')} - {axie.get('name')} (Clase: {axie.get('class')})"
            )
            print(f"    → Similar: #{match['id']} | Precio: ${r['price']:.2f} USD")
            print(f"    → Metodología: {r['nivel']}")
            print(
                f"    → Enlace: https://app.axieinfinity.com/marketplace/axies/{match['id']}/"
            )
            print()

    print("=" * 60)


def main():
    print("=== ESTIMADOR DE VALOR AXIE ===")
    print("1. Buscar por URL de Axie (marketplace)")
    print("2. Buscar por dirección de billetera")

    option = input("\nSeleccione opción (1/2): ").strip()

    if option == "1":
        # Buscar por URL
        url_input = input("\nIntrodúzca la URL del Axie: ").strip()
        if not url_input:
            url_input = "https://app.axieinfinity.com/marketplace/axies/5563211/"

        axie_id = reap_axie_id_from_url(url_input)
        if not axie_id:
            print("[!] URL no válida.")
            return

        process_single_axie(axie_id)

    elif option == "2":
        # Buscar por billetera
        wallet_input = input(
            "\nIntrodúzca la dirección de billetera (ronin:0x... o URL de perfil): "
        ).strip()
        if not wallet_input:
            print("[!] Debe ingresar una dirección de billetera.")
            return

        process_wallet(wallet_input)

    else:
        print("[!] Opción inválida.")


if __name__ == "__main__":
    main()

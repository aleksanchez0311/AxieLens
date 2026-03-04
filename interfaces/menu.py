import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para poder importar los módulos
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from core.logic import AxieLogic
from core.utils import (
    format_ronin_address,
    format_currency,
    get_axie_url,
    get_wallet_url,
)

# Inicializar lógica central
logic = AxieLogic()


def format_axie_message(data):
    """Genera el bloque de texto para un Axie en formato consola de forma optimizada."""

    axie_id = data.get("id")
    similar_id = data.get("similar_axie_id")
    curr_addr = data.get("owner_of")
    first_addr = data.get("first_owner")
    val = data.get("valuation", {})

    metadata = data.get("metadata", {})
    properties = metadata.get("properties", {})
    clase = properties.get("class", "N/A")

    valuacion = format_currency(val.get("valuation_usd", 0))
    metodo = val.get("method", "N/A")

    axie_url = get_axie_url(axie_id) if axie_id else "N/A"
    similar_axie_url = get_axie_url(similar_id) if similar_id else "N/A"
    curr_addr_url = get_wallet_url(curr_addr) if curr_addr else "N/A"

    if first_addr:
        first_addr_url = get_wallet_url(first_addr)
        first_name = logic.get_owner_name(first_addr)
    else:
        first_addr_url = "N/A"
        first_name = "N/A"

    lines = [
        "-" * 60,
        f"AXIE #{axie_id} | CLASE: {clase}",
        f"PRIMER DUEÑO: {first_name}",
        f"BILLETRA DEL PRIMER DUEÑO: {first_addr_url}",
        f"BILLETRA DEL DUEÑO ACTUAL: {curr_addr_url}",
        f"AXIE URL: {axie_url}",
        f"SIMILAR AXIE URL: {similar_axie_url}",
        f"VALUACIÓN: {valuacion}",
        f"MÉTODO: {metodo}",
    ]
    return "\n".join(lines)


def main():
    while True:
        print("\n" + "=" * 30)
        print("   AXIE CLASIFIER - MENU")
        print("=" * 30)
        print("1. Consultar Axie por ID")
        print("2. Listar Billetera (Detalle)")
        print("3. Resumen de Billetera (Total)")
        print("0. Salir")

        op = input("\nSeleccione una opción: ")

        if op == "0":
            print("Saliendo...")
            break

        elif op == "1":
            idx = input("Ingrese ID del Axie: ")
            data = logic.get_complete_axie_data(idx)
            if data:
                print(format_axie_message(data))
            else:
                print("[!] Axie no encontrado.")

        elif op == "2":
            addr = input("Ingrese dirección 0x ")
            print(f"[*] Consultando axies de {logic.get_owner_name(addr) or addr}...")
            axies = logic.get_all_axies_from_wallet(addr)

            if not axies:
                print("[!] No se encontraron axies adultos.")
                continue

            for a in axies:
                a_id = a.get("token_id") or a.get("id")
                data = logic.get_complete_axie_data(a_id)
                if data:
                    print(format_axie_message(data))

        elif op == "3":
            addr = input("Ingrese dirección 0x ")
            print(
                f"[*] Calculando resumen para {logic.get_owner_name(addr) or addr}..."
            )
            summary = logic.calculate_wallet_summary(addr)

            print("\n" + "*" * 40)
            print(f" RESUMEN: {summary['owner_name'] or 'Desconocido'}")
            print(f" TOTAL AXIES: {summary['total_axies']}")
            print(f" VALOR TOTAL: {format_currency(summary['total_valuation_usd'])}")
            print("*" * 40)

        else:
            print("[!] Opción inválida.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProceso detenido.")

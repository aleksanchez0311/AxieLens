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
    curr_addr = data.get("current_owner_address")
    first_addr = data.get("first_owner")
    val = data.get("valuation", 0.0)

    clase = data.get("class_name", "N/A")

    valuacion = format_currency(val)
    metodo = data.get("valuation_method", "Calculado")

    axie_url = get_axie_url(axie_id) if axie_id else "N/A"
    
    # Usar la billetera actual (curr_addr) para el enlace si es una billetera
    # Para similar, asumimos que es un Axie ID, así que usamos get_axie_url
    # El bug original era que similar_id era el ID del Axie pero se usaba para wallet_url
    # Por lo tanto, debería ser get_axie_url
    # PERO si el axie similar no existe o es None, puede fallar o ser incorrecto.
    # Revisemos si en el output dice "Similar Axie URL: ...7544097"
    # "7544097" es el ID del axie, NO la billetera. Asi que get_axie_url es correcto.
    # El ID del similar debería ser un ID de Axie, pero si por alguna razón
    # es una dirección de billetera (raro), usaríamos get_wallet_url.
    # En la mayoría de los casos, get_axie_url es correcto.
    if similar_id and isinstance(similar_id, str) and len(similar_id) > 15:
        similar_axie_url = get_wallet_url(similar_id)
    else:
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
        f"AXIE {axie_id} | CLASE: {clase}",
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
        print("   AXIE LENS - MENU")
        print("=" * 30)
        print("1. Consultar Axie por ID")
        print("2. Listar Billetera (Detalle)")
        print("3. Resumen de Billetera (Total)")
        print("4. Actualizar lista de Billeteras")
        print("0. Salir")

        op = input("\nSeleccione una opción: ")

        if op == "0":
            print("Saliendo...")
            break

        elif op == "1":
            idx = input("Ingrese ID del Axie: ")
            try:
                data = logic.get_complete_axie_data(idx)
                if data:
                    print(format_axie_message(data))
                else:
                    print("[!] Axie no encontrado.")
            except ConnectionError as e:
                print(f"\n[!] {str(e)}")

        elif op == "2":
            addr = input("Ingrese dirección de billetera: ")
            print(f"[*] Consultando axies de {logic.get_owner_name(addr) or addr}...")
            axies = logic.get_all_axies_from_wallet(addr)

            if not axies:
                print("[!] No se encontraron axies adultos.")
                continue

            try:
                for data in axies:
                    # data ya debería tener toda la información (incluyendo valoración)
                    print(format_axie_message(data))
            except ConnectionError as e:
                print(f"\n[!] {str(e)}")

        elif op == "3":
            addr = input("Ingrese dirección de billetera: ")
            print(
                f"[*] Calculando resumen para {logic.get_owner_name(addr) or addr}..."
            )
            try:
                summary = logic.calculate_wallet_summary(addr)

                print("\n" + "*" * 40)
                print(f" RESUMEN: {summary['owner_name'] or 'Desconocido'}")
                print(f" TOTAL AXIES: {summary['total_axies']}")
                print(
                    f" VALOR TOTAL: {format_currency(summary['total_valuation_usd'])}"
                )
                print("*" * 40)
            except ConnectionError as e:
                print(f"\n[!] {str(e)}")

        elif op == "4":
            path = input("Ingrese la ruta absoluta del nuevo archivo JSON: ")
            try:
                with open(path.strip("\"' "), "r", encoding="utf-8") as f:
                    content = f.read()
                success, error = logic.update_owners_data(content)
                if success:
                    print("[*] ¡Lista de billeteras actualizada correctamente!")
                else:
                    print(f"[!] Error al actualizar JSON: {error}")
            except Exception as e:
                print(f"[!] Error leyendo el archivo: {e}")

        else:
            print("[!] Opción inválida.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProceso detenido.")

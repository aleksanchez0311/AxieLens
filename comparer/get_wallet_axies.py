from accesser.skymavis import _execute_request


def get_wallet_address_from_input(input_str):
    """Extrae la dirección de la billetera desde diferentes formatos de entrada."""
    import re

    input_str = input_str.strip()

    # Si ya es una dirección ronin (0x...)
    if input_str.startswith("0x"):
        return input_str

    # Si es una URL de marketplace o perfil
    if "axieinfinity.com" in input_str:
        # Buscar dirección ronin en URLs
        match = re.search(r"(0x[a-fA-F0-9]{40})", input_str)
        if match:
            return match.group(1)

        # Buscar en formato /profile/ronin-address
        match = re.search(r"/profile/(0x[a-fA-F0-9]{40})", input_str)
        if match:
            return match.group(1)

    return None


def fetch_wallet_axies(wallet_address):
    """
    Obtiene todos los axies de una billetera usando GetMiniProfileByRoninAddress.
    """
    query = """
    query GetAxiesByOwner($address: String!, $from: Int, $size: Int) {
      axies(owner: $address, criteria: {stages: [4]}, from: $from, size: $size) {
        total
        results {
          id
          name
          class
          bodyShape
          stage
          breedCount
          parts {
            id
            name
            class
            type
            stage
          }
        }
      }
    }
    """

    payload = {
        "operationName": "GetAxiesByOwner",
        "variables": {"address": wallet_address, "from": 0, "size": 100},
        "query": query,
    }

    print(f"[*] Obteniendo axies para: {wallet_address}")
    data = _execute_request(payload)

    if data and "axies" in data:
        result = data["axies"]
        total = result.get("total", 0)
        all_axies = result.get("results", [])

        print(f"[*] Encontrados {total} axies")

        # Obtener más páginas si hay más de 100
        if total > 100:
            for page in range(1, (total // 100) + 1):
                page_payload = {
                    "operationName": "GetAxiesByOwner",
                    "variables": {
                        "address": wallet_address,
                        "from": page * 100,
                        "size": 100,
                    },
                    "query": query,
                }
                page_data = _execute_request(page_payload)
                if page_data and "axies" in page_data:
                    all_axies.extend(page_data["axies"].get("results", []))

        return all_axies

    return None


def get_axies_for_comparison(wallet_address):
    """
    Obtiene los axies de una billetera y los prepara para comparación.
    Solo retorna axies que tienen partes (stage 4 = completamente crecido)
    """
    axies = fetch_wallet_axies(wallet_address)

    if not axies:
        return []

    # Filtrar solo axies completamente crecidos (stage 4)
    valid_axies = []
    for axie in axies:
        if axie.get("stage") == 4 and axie.get("parts"):
            valid_axies.append(axie)

    print(f"[*] {len(valid_axies)} axies listos para valoración (stage 4)")
    return valid_axies

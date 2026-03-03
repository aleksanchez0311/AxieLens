from accesser.skymavis import _execute_request


def fetch_axie_details(axie_id):
    """
    Obtiene detalles del Axie.
    Ajustado para manejar la estructura de datos real de Sky Mavis.
    """
    query = """
    query GetAxieDetail($axieId: ID!) {
      axie(axieId: $axieId) {
        id
        name
        class
        bodyShape
        parts {
          id
          name
          class
          type
          stage
        }
        partEvolutionInfo {
          partType
          status
        }
      }
    }
    """
    payload = {
        "operationName": "GetAxieDetail",
        "variables": {"axieId": str(axie_id)},
        "query": query,
    }

    data = _execute_request(payload)

    if data and "axie" in data:
        return data["axie"]

    # Si no viene en el nodo 'axie', buscamos en resultados generales por si acaso
    return None

from accesser.skymavis import _execute_request


def fetch_marketplace(criteria_dict):
    """
    Busca en el mercado usando el payload avanzado.
    """
    query = """
    query GetAxiesMarketplace($auctionType: AuctionType, $criteria: AxieSearchCriteria, $criterias: [AxieSearchCriteria!] = [], $from: Int, $sort: SortBy, $size: Int) {
      axies(
        auctionType: $auctionType
        criteria: $criteria
        criterias: $criterias
        from: $from
        sort: $sort
        size: $size
      ) {
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
        "criterias": [],
        "from": 0,
        "sort": "PriceAsc",
        "size": 50,
        "auctionType": "Sale",
        "criteria": criteria_dict,
    }

    payload = {
        "operationName": "GetAxiesMarketplace",
        "variables": variables,
        "query": query,
    }

    data = _execute_request(payload)

    # Retornamos el objeto 'axies' que contiene 'total' y 'results'
    if data and "axies" in data:
        return data["axies"]
    return None

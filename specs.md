# Especificaciones Técnicas - Axie Classifier

## Visión General

Axie Classifier es una aplicación que conecta con las APIs de Moralis y Sky Mavis para obtener datos de Axies NFT en la blockchain Ronin y calcular su valuación de mercado.

## APIs Utilizadas

### Moralis API

- **Propósito**: Obtener datos de Axies y billeteras
- **Endpoints**:
  - `/nft/{contract}/{token_id}` - Datos de un Axie
  - `/{wallet_address}/nft` - Axies de una billetera
  - `/nft/{contract}/{token_id}/transfers` - Historial de transferencias
- **Rate Limiting**: Reintento automático tras 1 segundo (código 429)
- **URL por defecto**: `https://deep-index.moralis.io/api/v2.2`
- **Contrato default**: `0x32953928646d7367332260ed41ce1841f3e97910`

### Sky Mavis GraphQL API

- **Propósito**: Búsqueda en marketplace y valuación
- **Query Principal**: `GetAxiesMarketplace`
- **Ordenamiento**: PriceAsc (precio ascendente)
- **Autenticación**: Bearer token + API Key + Cookie
- **URL Base del Marketplace**: `https://app.axieinfinity.com/marketplace/axies/`

## Algoritmo de Valuación

### Flujo de Búsqueda de Similares

El algoritmo utiliza un sistema de fallback progresivo con 6 pasos:

1. **Paso 0**: Clase + Forma + 12 partes (dual base/EVO)
2. **Paso 1**: Exacto (Forma/Clase/Evo)
3. **Paso 2**: Clase + Partes (Sin Forma)
4. **Paso 5**: Clase + Partes Base
5. **Paso 6**: Solo Partes Base
6. **Paso 9**: Core 4 (Mouth, Horn, Back, Tail)

### Cálculo de Valuación

- Se obtienen los 10 Axies más baratos que coinciden con los criterios
- Se calcula la **mediana** de los precios en USD
- Se genera URL de marketplace para el Axie encontrado

### Detección de Evolución

- **ID Base**: Se limpia el sufijo `-2` del ID de parte usando regex
- **ID EVO**: Se añade `-2` al ID base para obtener versión evolucionada
- El sistema busca tanto versiones base como EVO de cada parte

## Estructura de Datos

### Axie (desde Moralis)

```json
{
  "id": "token_id",
  "owner_of": "dirección_wallet",
  "metadata": {
    "properties": {
      "class": "Beast|Plant|Aquat|Insect|Bird|Reptile",
      "stage": 4,
      "bodyShape": "Slim|Fat"
    }
  },
  "parts": [
    { "type": "Eyes|Ears|Mouth|Horn|Back|Tail", "id": "...", "stage": 1 }
  ]
}
```

### Valuación

```json
{
  "axie": { ... },
  "valuation_usd": 0.0,
  "similar_axie_id": "id_del_match",
  "method": "descripción_del_paso",
  "total_found": 0,
  "similars_url": "url_de_búsqueda",
  "similar_axie_url": "url_del_axie_encontrado"
}
```

### Resumen de Billetera

```json
{
  "owner_name": "Nombre o None",
  "total_axies": 0,
  "total_valuation_usd": 0.0,
  "axies": [ ... ]
}
```

## Componentes del Sistema

### app.py

- Punto de entrada principal (orquestador)
- Inicia 3 procesos en paralelo:
  1. Servidor web (hilo)
  2. Bot de Telegram (subprocess)
  3. Menú de consola (subprocess)
- Manejo de limpieza al salir (KeyboardInterrupt)

### core/logic.py

- Clase `AxieLogic`: Coordina Moralis y Sky Mavis
- Métodos:
  - `load_owners_data()`: Carga wallets_for_first_owner_finding.json
  - `get_owner_name(address)`: Busca nombre de owner
  - `get_first_owner(axie_id)`: Rastrea historial de transferencias
  - `get_complete_axie_data(axie_id)`: Datos completos + valoración + primer dueño
  - `get_all_axies_from_wallet(address)`: Axies adultos (stage == 4)
  - `calculate_wallet_summary(address)`: Resumen económico

### core/moralis.py

- Clase `Moraliscore`
- Métodos:
  - `get_axie_by_id(axie_id)`: Datos de un Axie
  - `get_wallet_axies(address)`: Axies de billetera
  - `get_nft_transfers(token_id)`: Historial de transferencias
- Rate limiting: 1 segundo de espera en código 429

### core/skymavis.py

- Clase `SkyMaviscore`
- Métodos:
  - `fetch_marketplace(criteria_dict, size)`: Búsqueda GraphQL
  - `search_similar_axies(base_axie)`: Algoritmo de similares
  - `get_axie_valuation(base_axie)`: Wrapper público
- Manejo de errores silencioso (retorna None en fallos)

### core/utils.py

- `load_env()`: Carga variables desde .env
- `format_ronin_address(address)`: Convierte 0x a ronin:
- `format_currency(amount)`: Formato USD
- `get_axie_url(axie_id)`: URL del marketplace
- `get_wallet_url(address)`: URL del perfil

### interfaces/bot.py

- Bot Telegram con `ConversationHandler`
- Estados: CHOOSING, TYPING_ID, TYPING_WALLET_VIEW, TYPING_WALLET_SUMMARY
- Autenticación opcional por `TELEGRAM_CHAT_ID`
- Teclado interactivo con botones

### interfaces/menu.py

- Menú de consola interactivo
- Opciones:
  1. Consultar Axie por ID
  2. Listar Billetera (Detalle)
  3. Resumen de Billetera (Total)
  4. Salir

### interfaces/server.py

- Servidor Flask
- Puerto 5000 por defecto
- Rutas: `/`, `/privacy`, `/terms`
- Usa threading para ejecución en segundo plano

## Variables de Entorno

| Variable              | Requerido | Default                                    | Descripción                 |
| --------------------- | --------- | ------------------------------------------ | --------------------------- |
| MORALIS_API_KEY       | Sí        | -                                          | API key de Moralis          |
| MORALIS_URL           | No        | https://deep-index.moralis.io/api/v2.2     | Endpoint de Moralis         |
| CONTRACT              | No        | 0x32953928646d7367332260ed41ce1841f3e97910 | Dirección del contrato Axie |
| CHAIN                 | No        | ronin                                      | Red (ronin)                 |
| SKYMAVIS_API_KEY      | Sí        | -                                          | API key de Sky Mavis        |
| AXIE_MARKETPLACE_BASE | Sí        | -                                          | URL base del marketplace    |
| GRAPHQL_URL           | Sí        | -                                          | Endpoint GraphQL            |
| BEARER                | Sí        | -                                          | Token de autenticación      |
| COOKIE_VALUE          | Sí        | -                                          | Cookie de sesión            |
| TELEGRAM_TOKEN        | No        | -                                          | Token del bot               |
| TELEGRAM_CHAT_ID      | No        | -                                          | ID de chat autorizado       |

## Rate Limiting

- **Moralis**: 1 segundo de espera en código 429, luego reintento automático
- **Sky Mavis**: Manejo básico de errores (retorna None)

## Limitaciones Conocidas

1. Las peticiones a Sky Mavis pueden fallar silenciosamente (retornan None)
2. El proyecto debe ejecutarse desde la raíz (imports absolutos)
3. El bot de Telegram procesa máximo 15 Axies por billetera (límite de seguridad)
4. Se añade delay de 0.4s entre mensajes al enviar Axies a Telegram

## Archivo wallets_for_first_owner_finding.json

Para mapear direcciones a nombres legibles, crear `wallets_for_first_owner_finding.json` en la raíz:

```json
{
  "Juan Perez": {
    "ronin": "ronin:abc123...",
    "0x": "0xabc123..."
  }
}
```

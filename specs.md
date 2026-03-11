# Especificaciones Técnicas - Axie Lens

## Visión General

Axie Lens es una aplicación que conecta con la API de Sky Mavis para obtener datos de Axies NFT en la blockchain Ronin y calcular su valuación de mercado. El sistema utiliza una arquitectura Python → Node.js donde Python orquesta las llamadas a scripts JavaScript que realizan las peticiones a la API.

## Arquitectura del Sistema

### Flujo de Datos

```
Python (app.py, logic.py)
    ↓ 调用
Python (endpoint.py) - Wrapper
    ↓ subprocess.run(env=...)
Node.js (endpoint.js) - API calls
    ↓ HTTP
Sky Mavis GraphQL API
```

## APIs Utilizadas

### Sky Mavis GraphQL API

- **Propósito**: Obtener datos de Axies, billeteras y búsqueda en marketplace
- **Endpoints**:
  - `https://api-gateway.skymavis.com/graphql/axie-marketplace` - Datos de Axies
- **Autenticación**: API Key en header `x-api-key`
- **Clase**: `endpoint.js` (funciones getAxieDetails, getWalletAxies, getSimilarAxies)

## Algoritmo de Valuación

### Flujo de Búsqueda de Similares

El algoritmo utiliza un sistema de fallback progresivo con 7 pasos:

1. **bodyShape + class + parts** (original)
2. **class + parts** (sin bodyShape)
3. **class + parts sin eyes**
4. **class + parts sin ears**
5. **sin eyes y ears**
6. **solo parts** (sin class)
7. Si no hay resultados, retorna vacío

### Cálculo de Valuación

- Se obtienen los 10 Axies más baratos que coinciden con los criterios
- Se calcula la **mediana** de los precios en USD
- Métodos disponibles: min, max, avg, median, floor, percentile75

## Estructura de Datos

### Axie (desde API)

```json
{
  "id": "9352681",
  "name": "Terminator",
  "class": "Reptile",
  "stage": 4,
  "owner": "0xcdd08182476f178f422a16a6be7cff0a1243de6c",
  "bodyShape": "Normal",
  "purity": 27,
  "parts": [
    { "id": "eyes-tricky", "name": "Tricky", "class": "Reptile", "type": "Eyes" },
    { "id": "ears-bubblemaker", "name": "Bubblemaker", "class": "Aquatic", "type": "Ears" }
  ],
  "stats": { "hp": 49, "morale": 44, "skill": 31, "speed": 40 },
  "order": { "currentPriceUsd": "5.50" },
  "transferHistory": {
    "results": [
      { "from": "0x3a27...", "to": "0x4948...", "timestamp": 1710558901 }
    ],
    "total": 3
  }
}
```

### Respuesta de Similares

```json
{
  "axies": [...],
  "criteria": "bodyShapes: Normal, classes: Reptile, parts: [...]",
  "total": 10
}
```

### Resumen de Billetera

```json
{
  "owner_name": "Juan Perez",
  "total_axies": 5,
  "axies": [...]
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

### core/endpoint.js

- API de Sky Mavis implementada en Node.js
- Funciones principales:
  - `getAxieDetails(axieId)`: Obtiene detalles de un Axie
  - `getWalletAxies(walletId, from, size)`: Obtiene Axies de una billetera
  - `getSimilarAxiesRaw(criteria, from, size)`: Busca axies similares
  - `getSimilarAxies(axie, from, size)`: Algoritmo recursivo de similares
  - `getAxieValuation(similarAxies, tipoCalculo)`: Calcula valoración
- Lee variables de entorno del proceso padre
- Maneja conversión de queries GraphQL internamente

### core/endpoint.py

- Wrapper Python que orquesta llamadas a `core/endpoint.js`
- Pasa variables de entorno usando el parámetro `env` de `subprocess.run()`
- Métodos:
  - `get_axie_details(axie_id)`: Wrapper de getAxieDetails
  - `get_wallet_axies(wallet_id, from, size)`: Wrapper de getWalletAxies
  - `get_similar_axies(axie, from, size)`: Wrapper de getSimilarAxies

### core/logic.py

- Clase `AxieLogic`: Coordina llamadas a endpoint.py
- Métodos:
  - `load_owners_data()`: Carga wallets_for_first_owner_finding.json
  - `update_owners_data(json_content)`: Actualiza el archivo JSON
  - `get_owner_name(address)`: Busca nombre de owner
  - `get_first_owner(axie_id)`: Rastrea historial de transferencias
  - `get_complete_axie_data(axie_id)`: Datos completos + valoración + primer dueño
  - `get_all_axies_from_wallet(address)`: Axies adultos (stage == 4)
  - `calculate_wallet_summary(address)`: Resumen económico

### core/utils.py

- `load_env()`: Carga variables desde .env
- `format_ronin_address(address)`: Convierte 0x a ronin:
- `format_currency(amount)`: Formato USD
- `get_axie_url(axie_id)`: URL del marketplace

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

| Variable                | Requerido | Default                                                                      | Descripción                       |
| ----------------------- | --------- | ---------------------------------------------------------------------------- | --------------------------------- |
| SKYMAVIS_API_KEY        | Sí        | -                                                                            | API key de Sky Mavis              |
| ENDPOINT_GRAPHQL        | No        | https://api-gateway.skymavis.com/graphql/axie-marketplace                    | Endpoint GraphQL de Axies         |
| TELEGRAM_TOKEN          | No        | -                                                                            | Token del bot                     |

## Rate Limiting

- La API de Sky Mavis puede retornar código 429 (Too Many Requests)
- Recomendación: agregar delays entre llamadas si se procesan muchas billeteras

## Limitaciones Conocidas

1. El proyecto debe ejecutarse desde la raíz (imports absolutos)
2. El bot de Telegram procesa máximo 15 Axies por billetera (límite de seguridad)
3. Se añade delay de 0.4s entre mensajes al enviar Axies a Telegram

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

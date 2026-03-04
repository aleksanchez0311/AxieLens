# Axie Classifier

Aplicación para valuar Axies NFT y analizar billeteras en el ecosistema Axie Infinity (Ronin).

## Características

- **Valuación de Axies**: Obtiene el valor de mercado de cualquier Axie basándose en Axies similares.
- **Análisis de Billeteras**: Muestra todos los Axies adultos de una billetera Ronin con sus valuaciones.
- **Resumen de Cartera**: Calcula el valor total de una colección de Axies.
- **Bot de Telegram**: Interfaz conversacional para consultas desde Telegram.
- **Servidor Web**: Panel web informativo disponible en el puerto 5000.
- **Tracking de Primer Dueño**: Rastrea el historial de transferencias para identificar el primer propietario.

## Requisitos

- Python 3.8+
- API keys de Moralis y Sky Mavis

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Configurar variables de entorno en `.env`:

```env
# Moralis API
MORALIS_API_KEY=tu_api_key
MORALIS_URL=https://deep-index.moralis.io/api/v2.2
CONTRACT=0x32953928646d7367332260ed41ce1841f3e97910
CHAIN=ronin

# Sky Mavis API
SKYMAVIS_API_KEY=tu_api_key
AXIE_MARKETPLACE_BASE=https://app.axieinfinity.com/marketplace/axies/
GRAPHQL_URL=https://graphql.axieinfinity.com/graphql
BEARER=tu_bearer
COOKIE_VALUE=tu_cookie

# Telegram (opcional)
TELEGRAM_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_chat_id
```

## Uso

```powershell
python app.py
```

Esto iniciarán:

1. Servidor web en segundo plano (puerto 5000)
2. Bot de Telegram en segundo plano
3. Menú interactivo en consola

### Menú Principal

1. Consultar Axie por ID
2. Listar Billetera (Detalle)
3. Resumen de Billetera (Total)
4. Salir

### Comandos del Bot de Telegram

- `/start` - Iniciar el bot (teclado interactivo)
- `/cancel` - Cancelar operación actual

**Botones interactivos:**

- 🔍 Buscar ID - Valuar Axie por ID
- 👛 Ver Wallet (Detalle) - Ver Axies en billetera
- 📊 Resumen Wallet - Resumen económico de billetera

## Estructura del Proyecto

```
AxieClasifier/
├── app.py                    # Punto de entrada principal (orquestador)
├── core/
│   ├── logic.py             # Capa de lógica de negocio (AxieLogic)
│   ├── skymavis.py         # API de Sky Mavis (Marketplace/Valuación)
│   ├── moralis.py          # API de Moralis (NFTs)
│   └── utils.py            # Utilidades (formato, URLs, .env)
├── interfaces/
│   ├── bot.py              # Bot de Telegram interactivo
│   ├── menu.py             # Menú de consola interactivo
│   └── server.py           # Servidor web Flask
└── templates/               # Plantillas HTML (index, privacy, terms)
```

## Algoritmo de Valuación

El sistema utiliza un algoritmo de fallback progresivo de 6 pasos para encontrar Axies similares:

1. **Paso 0**: Clase + Forma + 12 partes (dual base/EVO)
2. **Paso 1**: Exacto (Forma/Clase/Evo)
3. **Paso 2**: Clase + Partes (Sin Forma)
4. **Paso 5**: Clase + Partes Base
5. **Paso 6**: Solo Partes Base
6. **Paso 9**: Core 4 (Mouth/Horn/Back/Tail)

La valoración se calcula usando la mediana de precios de los 10 Axies más baratos encontrados.

## Archivo wallets_for_first_owner_finding.json

Para mapear direcciones a nombres legibles, crear `wallets_for_first_owner_finding.json` en la raíz:

```json
{
  "Juan Perez": {
    "ronin": "ronin:abc123...",
    "0x": "0xabc123..."
  },
  "CryptoKing": {
    "ronin": "ronin:def456...",
    "0x": "0xdef456..."
  }
}
```

## Licencia

MIT

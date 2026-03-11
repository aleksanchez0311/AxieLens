# Axie Lens

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
- Node.js 18+
- API key de Sky Mavis

## Instalación

1. Clonar el repositorio
2. Instalar dependencias Python:

```powershell
pip install -r requirements.txt
```

3. Configurar variables de entorno en `.env`:

```env
# Sky Mavis API (requerido)
SKYMAVIS_API_KEY=tu_api_key

# Endpoints GraphQL (opcionales)
ENDPOINT_GRAPHQL=https://api-gateway.skymavis.com/graphql/axie-marketplace

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

## Arquitectura

El sistema utiliza una arquitectura Python → Node.js:

```
Python (app.py, logic.py)
    ↓调用
Python (endpoint.py) - Wrapper
    ↓ subprocess.run(env=...)
Node.js (endpoint.js) - API calls
    ↓ HTTP
Sky Mavis GraphQL API
```

### core/endpoint.js

- API de Sky Mavis implementada en Node.js
- Funciones: getAxieDetails, getWalletAxies, getSimilarAxies

### core/endpoint.py

- Wrapper Python que orquesta llamadas a Node.js
- Pasa variables de entorno al proceso hijo

## Algoritmo de Valuación

El sistema utiliza un algoritmo de fallback progresivo de 7 pasos para encontrar Axies similares:

1. **bodyShape + class + parts** (original)
2. **class + parts** (sin bodyShape)
3. **class + parts sin eyes**
4. **class + parts sin ears**
5. **sin eyes y ears**
6. **solo parts** (sin class)
7. Si no hay resultados, retorna vacío

La valoración se calcula usando la mediana de precios de los 10 Axies más baratos encontrados.

## Estructura del Proyecto

```
AxieLens/
├── app.py                    # Punto de entrada principal (orquestador)
├── .env.example              # Ejemplo de variables de entorno
├── .gitignore                # Archivos ignorados por Git
├── AGENTS.md                 # Guía para agentes IA
├── README.md                 # Documentación principal
├── specs.md                  # Especificaciones técnicas
├── requirements.txt          # Dependencias Python
├── wallets_for_first_owner_finding.json.example  # Ejemplo de mapeo de owners
├── core/
│   ├── logic.py             # Capa de lógica de negocio (AxieLogic)
│   ├── endpoint.py          # Wrapper Python para endpoint.js
│   ├── endpoint.js          # API de Sky Mavis (Node.js)
│   └── utils.py             # Utilidades (formato, URLs, .env)
├── interfaces/
│   ├── bot.py               # Bot de Telegram interactivo
│   ├── menu.py              # Menú de consola interactivo
│   └── server.py            # Servidor web Flask
└── templates/               # Plantillas HTML (index, privacy, terms)
```

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

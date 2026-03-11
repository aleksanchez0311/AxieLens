# AGENTS.md

Este archivo proporciona orientación a los agentes que trabajan en este repositorio.

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

## Patrones No Obvios (Críticos)

### Integración Python → Node.js

- [`core/endpoint.py`](core/endpoint.py:1) orquesta las llamadas a [`core/endpoint.js`](core/endpoint.js:1)
- Las variables de entorno se pasan al proceso Node.js mediante el parámetro `env` de `subprocess.run()`
- El script Node.js debe ejecutarse siempre con las variables de entorno correctamente configuradas

### graphQLToJsonQuery.js

- [`core/endpoint.js`](core/endpoint.js:1) maneja la conversión de queries GraphQL internamente

### Variables de Entorno

- `SKYMAVIS_API_KEY` (requerido): API key de Sky Mavis
- `ENDPOINT_GRAPHQL` (opcional): Endpoint GraphQL de Axies

### Ejecución desde Raíz

- [`app.py`](app.py:1) usa imports absolutos. El proyecto **debe** ejecutarse siempre desde la raíz (`python app.py`).

### Algoritmo de Búsqueda de Similares (7 Pasos)

[`core/endpoint.js`](core/endpoint.js:1) utiliza un sistema de fallback progresivo:

1. **bodyShape + class + parts** (original)
2. **class + parts** (sin bodyShape)
3. **class + parts sin eyes**
4. **class + parts sin ears**
5. **sin eyes y ears**
6. **solo parts** (sin class)
7. Si no hay resultados, retorna vacío

### Tracking del Primer Dueño

- [`core/logic.py`](core/logic.py:1) implementa `get_first_owner()` que:
  1. Obtiene el historial de transferencias del Axie
  2. Busca primero si algún address en nuestra lista (`wallets_for_first_owner_finding.json`) aparece en el historial
  3. Si no hay match, usa el primer poseedor real (desde la dirección 0x000...)

### Archivo wallets_for_first_owner_finding.json

- [`core/logic.py:23-34`](core/logic.py:23) carga un archivo `wallets_for_first_owner_finding.json` en la raíz
- Formato esperado: `{ "NombreOwner": { "ronin": "ronin:...", "0x": "0x..." } }`
- Se usa para mostrar nombres legibles en lugar de direcciones.

### Menú de Consola

- [`interfaces/menu.py`](interfaces/menu.py:1) se ejecuta como proceso separado vía `subprocess.Popen`.
- Opciones: Consultar Axie por ID, Listar Billetera (detalle), Resumen de Billetera (total).
- Usa `AxieLogic` para obtener datos y formatea la salida para consola.

### Bot de Telegram

- [`interfaces/bot.py`](interfaces/bot.py:1) es un bot interactivo que corre en un proceso separado (`subprocess.Popen`).
- Usa `ConversationHandler` para manejar flujos de conversación.
- Incluye autenticación por `TELEGRAM_CHAT_ID` (opcional).
- Estados: CHOOSING, TYPING_ID, TYPING_WALLET_VIEW, TYPING_WALLET_SUMMARY

### Servidor Web

- [`interfaces/server.py`](interfaces/server.py:1) usa Flask para servir HTML desde `templates/` en el puerto 5000 por defecto.
- Rutas: `/`, `/privacy`, `/terms`.
- Se inicia en segundo plano al ejecutar `app.py`.

## Comandos

```powershell
# Iniciar aplicación completa (web + bot + menú)
python app.py
```

## Configuración (.env)

El archivo `.env` debe residir en la raíz y contener:

### APIs (Requerida)

- `SKYMAVIS_API_KEY`: API key de Sky Mavis

### APIs (Opcionales)

- `ENDPOINT_GRAPHQL`: Endpoint GraphQL de Axies (default: https://api-gateway.skymavis.com/graphql/axie-marketplace)

### Telegram (Opcional)

- `TELEGRAM_TOKEN`: Token del bot de Telegram

## Archivo wallets_for_first_owner_finding.json

ubicado en la raíz del proyecto, mapea nombres de owners a sus direcciones:

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

# AGENTS.md

Este archivo proporciona orientación a los agentes que trabajan en este repositorio.

## Estructura del Proyecto

- **app.py**: Punto de entrada principal. Orquestador que inicia servidor web, bot de Telegram y menú interactivo como procesos separados.
- **core/logic.py**: Capa de lógica de negocio. Coordina Moralis y Sky Mavis, maneja el tracking del primer dueño y el cálculo de resúmenes.
- **interfaces/menu.py**: Menú interactivo de consola para consultas locales.
- **interfaces/server.py**: Servidor web Flask que sirve las plantillas HTML.
- **core/**: Módulos de acceso a APIs externas.
  - **skymavis.py**: Conexión a Sky Mavis GraphQL API (Marketplace/Valuación).
  - **moralis.py**: Conexión a Moralis API (datos de NFTs y billeteras).
  - **utils.py**: Utilidades compartidas (formateo de direcciones, moneda, URLs, carga de variables de entorno).
- **interfaces/**: Módulos de mensajería.
  - **bot.py**: Bot de Telegram interactivo con menú y comandos.
- **templates/**: Plantillas HTML para el servidor web (index.html, privacy.html, terms.html).

## Patrones No Obvios (Críticos)

### API Keys con Defaults Vacíos

- [`core/skymavis.py:13-19`](core/skymavis.py:13) - `AXIE_MARKETPLACE_BASE`, `SKYMAVIS_API_KEY`, `GRAPHQL_URL`, `BEARER`, `COOKIE_VALUE` se leen con `os.environ.get()` y default `""`. Si faltan, las peticiones fallan silenciosamente.

- [`core/moralis.py:9-18`](core/moralis.py:9) - `MORALIS_API_KEY`, `MORALIS_URL`, `CONTRACT`, `CHAIN` se leen con `os.environ.get()` y tienen valores por defecto:
  - `MORALIS_URL` default: `https://deep-index.moralis.io/api/v2.2`
  - `CONTRACT` default: `0x32953928646d7367332260ed41ce1841f3e97910`
  - `CHAIN` default: `ronin`

### Ejecución desde Raíz

- [`app.py`](app.py:1) usa imports absolutos. El proyecto **debe** ejecutarse siempre desde la raíz (`python app.py`).

### Rate Limiting

- [`core/moralis.py:25-27`](core/moralis.py:25) implementa un reintento automático tras 1 segundo si recibe un error 429 (Too Many Requests).

### Manejo de Errores Silencioso

- [`core/skymavis.py:34-45`](core/skymavis.py:34) retorna `None` en fallos de red o GraphQL sin lanzar excepciones.

### Algoritmo de Búsqueda de Similares (6 Pasos)

[`core/skymavis.py:81-192`](core/skymavis.py:81) utiliza un sistema de fallback progresivo simplificado:

1. **Paso 0**: Clase + Forma + 12 partes (dual base/EVO)
2. **Paso 1**: Exacto (Forma/Clase/Evo)
3. **Paso 2**: Clase + Partes (Sin Forma)
4. **Paso 5**: Clase + Partes Base
5. **Paso 6**: Solo Partes Base
6. **Paso 9**: Core 4 (Mouth/Horn/Back/Tail)

### Detección de Evolución

- [`core/skymavis.py:94-99`](core/skymavis.py:94) proporciona funciones para obtener IDs base y EVO de partes:
  - `get_base_id(part)`: Limpia sufijos `-2` del ID usando regex
  - `get_evo_id(part)`: Añade `-2` para versión EVO

### Paginación en Moralis

- [`core/moralis.py:49-61`](core/moralis.py:49) maneja la obtención de NFTs de billeteras mediante `cursor`.

### Filtrado de Axies

- [`core/logic.py:84-90`](core/logic.py:84) filtra axies por `stage == 4` (Adultos) al obtener de billeteras.

### Tracking del Primer Dueño

- [`core/logic.py:50-72`](core/logic.py:50) implementa `get_first_owner()` que:
  1. Obtiene el historial de transferencias del Axie mediante `get_nft_transfers()`
  2. Busca primero si algún address en nuestra lista (`wallets_for_first_owner_finding.json`) aparece en el historial
  3. Si no hay match, usa el primer poseedor real (desde la dirección 0x000...)

### Archivo wallets_for_first_owner_finding.json

- [`core/logic.py:25-36`](core/logic.py:25) carga un archivo `wallets_for_first_owner_finding.json` en la raíz que mapea nombres de owners a sus billeteras.
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

### APIs (Requeridas)

- `MORALIS_API_KEY`: Para obtener datos de NFTs y carteras.
- `MORALIS_URL`: Endpoint de Moralis (ej: https://deep-index.moralis.io/api/v2.2)
- `CONTRACT`: Dirección del contrato Axie Ronin (default: 0x32953928646d7367332260ed41ce1841f3e97910)
- `CHAIN`: Red (ej: ronin)

- `SKYMAVIS_API_KEY`: Para consultas al Marketplace/Valuación.
- `AXIE_MARKETPLACE_BASE`: URL base del marketplace (ej: https://app.axieinfinity.com/marketplace/axies/)
- `GRAPHQL_URL`: Endpoint GraphQL de Sky Mavis
- `BEARER` y `COOKIE_VALUE`: Necesarios para ciertas peticiones a Sky Mavis.

### Telegram (Opcional - para notificaciones)

- `TELEGRAM_TOKEN`: Token del bot de Telegram.
- `TELEGRAM_CHAT_ID`: ID de chat autorizado (si está vacío, permite cualquier usuario).

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

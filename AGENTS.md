# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Patrones No Obvios (Críticos)

- **API keys con defaults vacíos**: [`accesser/skymavis.py:4-8`](accesser/skymavis.py:4) usa `os.environ.get()` con strings vacíos. Si no existen en `.env`, las requests fallan silenciosamente con error 401/403.

- **Ejecutar desde raíz del proyecto**: [`app.py:13`](app.py:13) modifica `sys.path`. Debe ejecutarse desde la raíz donde están las carpetas `finder/`, `comparer/`.

- **Stage 4 obligatorio**: [`comparer/get_wallet_axies.py:106`](comparer/get_wallet_axies.py:106) filtra `axie.get("stage") == 4` - solo axies completamente crecidos se valoran.

- **Algoritmo de 9 pasos**: [`comparer/get_market_comparison.py:5-19`](comparer/get_market_comparison.py:5) usa fallback progresivo: partes exactas → sin místicas → sin clase → sin ojos/orejas → solo 4 partes base.

- **Silent failures en requests**: [`accesser/skymavis.py:26-52`](accesser/skymavis.py:26) retorna `None` en errores 401/403/500 sin lanzar excepciones. Los errores solo se print.

- **Rate limiting**: [`ownerizer/get_first_owner_from_data.py:133`](ownerizer/get_first_owner_from_data.py:133) tiene `time.sleep(2)` entre requests a Moralis.

- **Bare except oculta errores**: [`messenger/send_telegram_message.py:18-20`](messenger/send_telegram_message.py:18) y [`ownerizer/get_first_owner_from_data.py:70,80`](ownerizer/get_first_owner_from_data.py:70) usan `except:` que oculta fallos silenciosamente.

- **Import mismatch**: [`app.py:5`](app.py:5) importa `from comparer.get_axie_details` pero el archivo está en `finder/get_axie_details.py`.

## Configuración

- Requiere `.env` en raíz: `SKYMAVIS_API_KEY`, `BEARER`, `COOKIE_VALUE`, `GRAPHQL_URL`
- Ownerizer requiere adicional: `MORALIS_API_KEY`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`

No hay tests, lint ni build system.

import os
import asyncio
import logging
import sys
from pathlib import Path

# Añadir el directorio raíz al path para poder importar los módulos
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from core.logic import AxieLogic
from core.utils import (
    format_ronin_address,
    format_currency,
    get_axie_url,
    get_wallet_url,
)

# Configuración de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)

# Inicializar lógica central y tokens
logic = AxieLogic()
TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

# Estados de la conversación
(
    CHOOSING,
    TYPING_ID,
    TYPING_WALLET_VIEW,
    TYPING_WALLET_SUMMARY,
    AWAITING_WALLETS_JSON,
) = range(5)


def format_axie_message_tg(data):
    """Genera el bloque de texto para un Axie en formato consola de forma optimizada."""

    axie_id = data.get("id")
    similar_id = data.get("similar_axie_id")
    curr_addr = data.get("current_owner_address")
    first_addr = data.get("first_owner")
    val = data.get("valuation", 0.0)

    metadata = data.get("metadata", {})
    # Usar los nuevos campos directamente
    clase = data.get("class_name", "N/A")

    valuacion = format_currency(val)
    metodo = data.get("valuation_method", "Calculado")

    axie_url = get_axie_url(axie_id) if axie_id else "N/A"
    # El ID del similar debería ser un ID de Axie, pero si por alguna razón
    # es una dirección de billetera (raro), usaríamos get_wallet_url.
    if similar_id and isinstance(similar_id, str) and len(similar_id) > 15:
        similar_axie_url = get_wallet_url(similar_id)
    else:
        similar_axie_url = get_axie_url(similar_id) if similar_id else "N/A"
    curr_addr_url = get_wallet_url(curr_addr) if curr_addr else "N/A"

    if first_addr:
        first_addr_url = get_wallet_url(first_addr)
        first_name = logic.get_owner_name(first_addr)
    else:
        first_addr_url = "N/A"
        first_name = "N/A"

    msg = [
        f"👾 {axie_url}",
        f"👾 *Axie {axie_id}* ({clase})",
        f"👶 *Primer Dueño:* {first_name}",
        f"👶 🔗 [Ver en Marketplace] *URL Primer Dueño:* {first_addr_url}",
        f"👤 🔗 [Ver en Marketplace] *URL Dueño Actual:* {curr_addr_url}",
        f"👾 🔗 [Ver Axie Similar]({similar_axie_url})",
        f"💰 *Valuación:* {valuacion}",
        f"🔍 *Método:* {metodo}",
    ]
    return "\n".join(msg)


# --- Manejadores de Comandos y Mensajes ---


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el bot y muestra el teclado principal."""
    reply_keyboard = [
        ["🔍 Buscar ID"],
        ["👛 Ver Wallet (Detalle)", "📊 Resumen Wallet"],
        ["🔄 Actualizar Billeteras"],
    ]
    await update.message.reply_text(
        "🚀 *Axie Lens Bot*\n¿Qué deseas hacer hoy?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
        parse_mode="Markdown",
    )
    return CHOOSING


async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la selección del menú principal."""
    text = update.message.text
    if text == "🔍 Buscar ID":
        await update.message.reply_text(
            "🔢 Envía el *ID del Axie*:", parse_mode="Markdown"
        )
        return TYPING_ID
    elif text == "👛 Ver Wallet (Detalle)":
        await update.message.reply_text(
            "📍 Envía la *dirección Ronin* para ver el detalle:", parse_mode="Markdown"
        )
        return TYPING_WALLET_VIEW
    elif text == "📊 Resumen Wallet":
        await update.message.reply_text(
            "📉 Envía la *dirección Ronin* para ver el resumen total:",
            parse_mode="Markdown",
        )
        return TYPING_WALLET_SUMMARY
    elif text == "🔄 Actualizar Billeteras":
        await update.message.reply_text(
            "📁 *Actualizar JSON de Billeteras*\nEnvía el nuevo archivo `.json` o pega el contenido JSON como texto directamente:",
            parse_mode="Markdown",
        )
        return AWAITING_WALLETS_JSON
    else:
        await update.message.reply_text("Opción no válida. Usa el teclado inferior.")
        return CHOOSING


async def process_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa un ID individual."""
    a_id = update.message.text.strip()
    if not a_id.isdigit():
        await update.message.reply_text("❌ El ID debe ser un número.")
        return TYPING_ID

    await update.message.reply_text(f"⏳ Analizando Axie #{a_id}...")
    try:
        data = logic.get_complete_axie_data(a_id)
        if data:
            await update.message.reply_text(
                format_axie_message_tg(data), parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Axie no encontrado.")
    except ConnectionError as e:
        await update.message.reply_text(
            f"❌ *{str(e)}*\n\n"
            "🔑 *Actualizar Credenciales de Sky Mavis*\n\n"
            "Envía el `BEARER` y la `COOKIE_VALUE` separados por una línea vacía.",
            parse_mode="Markdown",
        )
        return AWAITING_CREDENTIALS

    return await start(update, context)


async def process_wallet_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el detalle de todos los Axies en la billetera."""
    addr = update.message.text.strip()
    owner_name = logic.get_owner_name(addr)

    await update.message.reply_text(
        f"⏳ Consultando detalle de {owner_name or addr}..."
    )
    axies = logic.get_all_axies_from_wallet(addr)

    if not axies:
        await update.message.reply_text("❌ No se encontraron Axies adultos.")
    else:
        await update.message.reply_text(f"📦 Procesando {len(axies)} Axies...")
        try:
            for data in axies[:15]:  # Límite de seguridad
                # data ya debería tener toda la información
                await update.message.reply_text(
                    format_axie_message_tg(data), parse_mode="Markdown"
                )
                await asyncio.sleep(0.4)
        except ConnectionError as e:
            await update.message.reply_text(
                f"❌ *{str(e)}*",
                parse_mode="Markdown",
            )
            return await start(update, context)

    return await start(update, context)


async def process_wallet_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra solo el resumen económico y conteo de la billetera."""
    addr = update.message.text.strip()
    try:
        summary_data = logic.calculate_wallet_summary(addr)

        if summary_data["total_axies"] == 0:
            await update.message.reply_text("❌ Billetera vacía.")
        else:
            summary = [
                f"📊 *RESUMEN DE CUENTA*",
                f"👤 *Dueño:* {summary_data['owner_name'] or 'Desconocido'}",
                f"📍 *Ronin:* `{format_ronin_address(addr)}`",
                f"👾 *Total Axies:* {summary_data['total_axies']}",
                f"💰 *Valor Estimado:* {format_currency(summary_data['total_valuation_usd'])}",
            ]
            await update.message.reply_text("\n".join(summary), parse_mode="Markdown")

    except ConnectionError as e:
        await update.message.reply_text(
            f"❌ *{str(e)}*",
            parse_mode="Markdown",
        )

    return await start(update, context)


async def process_wallets_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el documento o texto JSON enviado."""
    content = ""
    try:
        if update.message.document:
            doc = update.message.document
            if not doc.file_name.endswith(".json"):
                await update.message.reply_text(
                    "❌ El archivo debe tener extensión .json. Intenta de nuevo:"
                )
                return AWAITING_WALLETS_JSON

            file = await context.bot.get_file(doc.file_id)
            byte_array = await file.download_as_bytearray()
            content = byte_array.decode("utf-8")
        elif update.message.text:
            content = update.message.text
        else:
            await update.message.reply_text(
                "❌ Formato no reconocido. Envía un archivo JSON o pega el texto. Intenta de nuevo:"
            )
            return AWAITING_WALLETS_JSON
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error al descargar o leer el archivo:\n{str(e)}\nIntenta de nuevo:"
        )
        return AWAITING_WALLETS_JSON

    success, error = logic.update_owners_data(content)
    if success:
        await update.message.reply_text(
            "✅ ¡Lista de billeteras de dueños actualizada correctamente!"
        )
        return await start(update, context)
    else:
        await update.message.reply_text(
            f"❌ Error al procesar y guardar el JSON:\n{error}\nIntenta de nuevo enviando un JSON válido:"
        )
        return AWAITING_WALLETS_JSON

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la operación actual."""
    await update.message.reply_text(
        "Operación cancelada.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    if not TOKEN:
        logging.error("TELEGRAM_TOKEN no configurado.")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND), handle_menu_choice)
            ],
            TYPING_ID: [MessageHandler(filters.TEXT & ~(filters.COMMAND), process_id)],
            TYPING_WALLET_VIEW: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND), process_wallet_view)
            ],
            TYPING_WALLET_SUMMARY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND), process_wallet_summary
                )
            ],
            AWAITING_WALLETS_JSON: [
                MessageHandler(
                    (filters.TEXT | filters.Document.ALL) & ~(filters.COMMAND),
                    process_wallets_json,
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()

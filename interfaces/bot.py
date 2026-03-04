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
AUTHORIZED_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Estados de la conversación
CHOOSING, TYPING_ID, TYPING_WALLET_VIEW, TYPING_WALLET_SUMMARY = range(4)


def format_axie_message_tg(data):
    """Genera el bloque de texto para un Axie en formato consola de forma optimizada."""

    axie_id = data.get("id")
    similar_id = data.get("similar_axie_id")
    curr_addr = data.get("owner_of")
    first_addr = data.get("first_owner")
    val = data.get("valuation", {})

    metadata = data.get("metadata", {})
    properties = metadata.get("properties", {})
    clase = properties.get("class", "N/A")

    valuacion = format_currency(val.get("valuation_usd", 0))
    metodo = val.get("method", "N/A")

    axie_url = get_axie_url(axie_id) if axie_id else "N/A"
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
        f"👾 *Axie #{axie_id}* ({clase})",
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
    ]
    await update.message.reply_text(
        "🚀 *Axie Classifier Bot*\n¿Qué deseas hacer hoy?",
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
    data = logic.get_complete_axie_data(a_id)
    if data:
        await update.message.reply_text(
            format_axie_message_tg(data), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Axie no encontrado.")

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
        for a in axies[:15]:  # Límite de seguridad
            a_id = a.get("token_id") or a.get("id")
            data = logic.get_complete_axie_data(a_id)
            if data:
                await update.message.reply_text(
                    format_axie_message_tg(data), parse_mode="Markdown"
                )
            await asyncio.sleep(0.4)

    return await start(update, context)


async def process_wallet_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra solo el resumen económico y conteo de la billetera."""
    addr = update.message.text.strip()
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

    return await start(update, context)


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
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()

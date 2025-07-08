import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import config

# Танзими логҳо
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Командаи /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Санҷиши обуна ба канал
    member = await context.bot.get_chat_member(config.REQUIRED_CHANNEL, user.id)
    if member.status not in ["member", "administrator", "creator"]:
        keyboard = [[InlineKeyboardButton("✅ Ман аъзо шудам", callback_data='check_sub')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔒 Барои истифодаи бот, аввал ба канали мо аъзо шавед:\n"
            f"{config.REQUIRED_CHANNEL_LINK}",
            reply_markup=reply_markup
        )
        return

    # Агар обуна бошад
    await update.message.reply_text(
        "🤖 Хуш омадед ба боти AI!\n\n"
        "- 🎨 Расм созед\n"
        "- 💬 Чат GPT\n"
        "- 🌍 Тарҷума кунед\n"
        "- 💳 Хариди VIP\n\n"
        "Менюро интихоб кунед."
    )

# Тугмаи 'Ман аъзо шудам'
async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    member = await context.bot.get_chat_member(config.REQUIRED_CHANNEL, user.id)
    if member.status not in ["member", "administrator", "creator"]:
        await query.answer("⛔ Шумо ҳанӯз обуна нашудаед.")
    else:
        await query.answer("✅ Ташаккур! Шумо ҳоло метавонед ботро истифода баред.")
        await query.edit_message_text("🎉 Дастрасӣ иҷозат дода шуд!")

# Оғози бот
def main():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_sub, pattern='check_sub'))

    app.run_polling()

if __name__ == '__main__':
    main()
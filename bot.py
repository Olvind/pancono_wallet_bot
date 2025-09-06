import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)
from dotenv import load_dotenv
from referral_manager import add_user
from wallet_manager import (
    create_wallet_for_user, get_balance,
    import_private_key, send_panca
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("🪙 Create Wallet", callback_data="create_wallet")],
        [InlineKeyboardButton("🔑 Import Private Key", callback_data="import_key")],
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance")],
        [InlineKeyboardButton("📤 Send PANCA", callback_data="send")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Welcome to Pancono Wallet Mini App!\nChoose an option below:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "create_wallet":
        wallet, passphrase = create_wallet_for_user(query.from_user.id)
        ref_link = f"https://t.me/{context.bot.username}?start={query.from_user.id}"
        await query.edit_message_text(
            f"✅ Wallet created!\n"
            f"Address: `{wallet}`\nPassphrase: `{passphrase}`\n\n"
            f"🔗 Your referral link:\n{ref_link}",
            parse_mode="Markdown"
        )

    elif query.data == "import_key":
        await query.edit_message_text("🔑 Send me the private key you want to import.")
        context.user_data["awaiting_key"] = True

    elif query.data == "balance":
        balances = get_balance(query.from_user.id)
        msg = "💰 *Your Balances:*\n"
        msg += f"Main Wallet: {balances['main']} PANCA\n"
        if balances["imported"]:
            msg += "\n🔑 Imported Keys:\n"
            for k, v in balances["imported"].items():
                msg += f"Key `{k}` → {v} PANCA\n"
        await query.edit_message_text(msg, parse_mode="Markdown")

    elif query.data == "send":
        await query.edit_message_text("📤 Enter recipient wallet and amount (format: `PANCA123456 50`).")
        context.user_data["awaiting_send"] = True

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_key"):
        key = update.message.text.strip()
        bal = import_private_key(update.effective_user.id, key)
        await update.message.reply_text(f"🔑 Key `{key}` imported!\nBalance: {bal} PANCA")
        context.user_data["awaiting_key"] = False

    elif context.user_data.get("awaiting_send"):
        try:
            wallet, amount = update.message.text.strip().split()
            amount = int(amount)
            success, msg = send_panca(update.effective_user.id, wallet, amount)
            await update.message.reply_text(msg)
        except Exception as e:
            await update.message.reply_text("❌ Invalid format. Use: `WalletID Amount`")
        context.user_data["awaiting_send"] = False

# ---------- Main ----------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

print("🚀 Bot is running...")
app.run_polling()

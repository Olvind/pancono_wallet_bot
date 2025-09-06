import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from referral_manager import add_user, add_referral
from wallet_manager import create_wallet_for_user

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = add_user(update.effective_user.id)
    await update.message.reply_text(
        f"Welcome to Pancono Wallet Demo!\n"
        f"Your referral code: {user['referral_code']}\n"
        f"Use /createwallet to generate your wallet."
    )

async def createwallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet, passphrase = create_wallet_for_user(update.effective_user.id)
    await update.message.reply_text(
        f"Wallet generated!\nAddress: {wallet}\nPassphrase: {passphrase}"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from referral_manager import load_db
    db = load_db()
    user = db["users"].get(str(update.effective_user.id))
    if not user:
        await update.message.reply_text("You do not have a wallet yet. Use /start")
        return
    await update.message.reply_text(f"Your balance: {user['balance']} PANCA")

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /referral <code>")
        return
    code = context.args[0]
    success = add_referral(update.effective_user.id, code)
    if success:
        await update.message.reply_text(f"Referral code applied successfully!")
    else:
        await update.message.reply_text(f"Invalid referral code.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("createwallet", createwallet))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("referral", referral))

print("Bot is running...")
app.run_polling()

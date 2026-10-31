import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ========= إعدادات البوت =========
# ضع توكن البوت تبعك من @BotFather هنا
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

# عنوان محفظة USDT TRC20 اللي يستقبل عليها الإيداعات
DEPOSIT_WALLET = "PUT_YOUR_TRC20_WALLET_HERE"

# خطط الاستثمار
PLANS = {
    "plan_7": {"name": "خطة 7 أيام", "days": 7, "profit": 15, "min": 10},
    "plan_15": {"name": "خطة 15 يوم", "days": 15, "profit": 35, "min": 50},
    "plan_30": {"name": "خطة 30 يوم", "days": 30, "profit": 80, "min": 100},
}

# قاعدة بيانات مؤقتة (في الذاكرة)
users_db = {}

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("💰 خطط الاستثمار", callback_data="plans")],
        [InlineKeyboardButton("📊 حسابي", callback_data="my_account"), InlineKeyboardButton("💳 إيداع", callback_data="deposit")],
        [InlineKeyboardButton("💸 سحب", callback_data="withdraw"), InlineKeyboardButton("👥 الإحالة", callback_data="referral")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0, "invested": 0, "profit": 0}
    
    text = f"""
🚀 *مرحباً بك في بوت استثمار USDT*

💵 استثمر USDT واربح أرباح يومية

{DEPOSIT_WALLET}

👇 اختر من القائمة:
"""
    await update.message.reply_text(text, reply_markup=get_main_menu(), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "plans":
        text = "📋 *خطط الاستثمار المتاحة:*\n\n"
        keyboard = []
        for key, plan in PLANS.items():
            text += f"🔹 *{plan['name']}*\n   المدة: {plan['days']} يوم\n   الربح: {plan['profit']}%\n   الحد الأدنى: {plan['min']} USDT\n\n"
            keyboard.append([InlineKeyboardButton(f"{plan['name']} - {plan['profit']}%", callback_data=key)])
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data.startswith("plan_"):
        plan = PLANS[query.data]
        text = f"""
✅ *{plan['name']}*

💰 الحد الأدنى: {plan['min']} USDT
📅 المدة: {plan['days']} يوم
📈 الربح الكلي: {plan['profit']}%

للبدء، أرسل المبلغ إلى محفظة الإيداع:
`{DEPOSIT_WALLET}`

شبكة: TRC20 (TRON)

بعد الإرسال اضغط تأكيد.
"""
        keyboard = [[InlineKeyboardButton("✅ أكدت الإيداع", callback_data="deposit"), InlineKeyboardButton("🔙 رجوع", callback_data="plans")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "deposit":
        text = f"""
💳 *الإيداع*

أرسل USDT (TRC20) إلى هذا العنوان:

`{DEPOSIT_WALLET}`

⚠️ تنبيه: أرسل فقط USDT على شبكة TRC20

بعد الإرسال، أرسل صورة التحويل للإدارة.
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "my_account":
        user_id = query.from_user.id
        data = users_db.get(user_id, {"balance": 0, "invested": 0, "profit": 0})
        text = f"""
📊 *حسابي*

💰 الرصيد: {data['balance']} USDT
📈 المستثمر: {data['invested']} USDT
💹 الأرباح: {data['profit']} USDT
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data in ["withdraw", "referral", "back"]:
        await query.edit_message_text("🚀 اختر من القائمة:", reply_markup=get_main_menu())

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()

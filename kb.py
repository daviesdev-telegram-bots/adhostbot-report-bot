from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


general_kb = ReplyKeyboardMarkup()
general_kb.add(KeyboardButton("🛍️Order Reports"))
general_kb.add(KeyboardButton("👤Account"), KeyboardButton("📞Support"))
cancel_kb = InlineKeyboardMarkup()
cancel_kb.add(InlineKeyboardButton("Cancel", callback_data="cancel"))

def back_btn(step="back"):
    return InlineKeyboardButton("back", callback_data=step)


class Admin:
    def back_btn(step="home"):
        return InlineKeyboardButton("back", callback_data="admin_" + step)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⌛Pending Orders", callback_data="admin_pending_orders"), InlineKeyboardButton("🚚 Shipped Orders", callback_data="admin_shipped_orders"))
    kb.add(back_btn())


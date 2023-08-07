from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from utils import report_violations

general_kb = ReplyKeyboardMarkup()
general_kb.add(KeyboardButton("🛍️Order Reports"))
general_kb.add(KeyboardButton("👤Account"), KeyboardButton("⏳Order History"))
general_kb.add(KeyboardButton("📞Support"))
cancel_kb = InlineKeyboardMarkup()
cancel_kb.add(InlineKeyboardButton("Cancel", callback_data="cancel"))

def report_kb(data):
    report_kb = InlineKeyboardMarkup(row_width=2)
    report_kb.add(*[InlineKeyboardButton(text, callback_data="violation:"+callback+":"+data) for callback, text in report_violations.items()])
    return report_kb

def back_btn(step="back"):
    return InlineKeyboardButton("back", callback_data=step)


class Admin:
    def back_btn(step="home"):
        return InlineKeyboardButton("back", callback_data="admin_" + step)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⌛Pending Orders", callback_data="admin_pending_orders"),
           InlineKeyboardButton("🚚 Shipped Orders", callback_data="admin_shipped_orders"))
    kb.add(back_btn())

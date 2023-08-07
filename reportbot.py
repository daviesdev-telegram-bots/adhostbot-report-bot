import json
import os

from dotenv import load_dotenv
from sellix import Sellix
from telebot import TeleBot
from telebot.types import CallbackQuery, Message, WebAppInfo

from kb import *
from models import User, session, Order

load_dotenv()

bot_token = os.getenv("bot_token")
owners = json.loads(os.getenv("owners"))
bot = TeleBot(bot_token, parse_mode="HTML")
sellix = Sellix(os.getenv("sellix_secret"), "banz")
support = "https://t.me/GetReportz"
admin_sellix_email = os.getenv("admin_sellix_email")
bot_username = bot.get_me().username

WEBHOOK_URL = "https://reportbot-one.vercel.app"

with open("socials.json") as f:
    socials = json.load(f)


def get_user(uid):
    user = session.query(User).get(str(uid))
    if not user:
        user = User(id=str(uid))
        session.add(user)
        session.commit()
    return user


def get_balance(user_id):
    user = session.query(User).get(str(user_id))
    return user.balance if user else 0.0


@bot.message_handler(["start"])
def start(message: Message):
    user = get_user(message.chat.id)
    bot.send_message(
        message.chat.id, f"<b>Lets get started🎉</b>\nUse the buttons below to begin using our report service.", reply_markup=general_kb)


@bot.message_handler(["admin"], func=lambda msg: msg.chat.id in owners)
def admin(message: Message):
    bot.send_message(
        message.chat.id, "Welcome to the admin panel.", reply_markup=Admin.kb)


@bot.message_handler(func=lambda msg: msg.text)
def all_messages(message: Message):
    if message.text == "🛍️Order Reports":
        kb = InlineKeyboardMarkup()
        kb.add(
            *[InlineKeyboardButton(i, callback_data=f"social:{i}") for i in socials])
        bot.send_message(
            message.chat.id, "What Social media do you want to order reports?", reply_markup=kb)
    elif message.text == "👤Account":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("➕Add balance",
               callback_data="self_add_balance"))
        user = get_user(message.chat.id)
        bot.send_message(message.chat.id,
                         f"<b>Welcome</b>.\n\n🪪Your ID: <code>{message.chat.id}</code>\n💲Balance: ${user.balance}",
                         reply_markup=kb)
    elif message.text == "⏳Order History":
        orders = session.query(Order).filter_by(user=str(message.chat.id)).order_by(
            Order.timestamp.desc()).limit(5).all()
        text = []
        if len(orders) == 0:
            text.append("You have no orders yet")

        for i in orders:
            text.append(f"Time: {i.timestamp.strftime('%I:%M %p %d %b, %Y')}\n"
                        f"Social: <b>{i.social_media} - {i.report_type}</b>\nNumber of reports: {i.value}\n"
                        f"Link: {i.link}\nStatus: {'Delivered✅' if i.shipped else 'Pending⌛'}")
        bot.send_message(
            message.chat.id, "<b>Order History</b>\n\n"+"\n\n".join(text))

    if message.text == "📞Support":
        bot.send_message(message.chat.id, f"Contact support: {support}", reply_markup=InlineKeyboardMarkup(
        ).add(InlineKeyboardButton("📞Support", url=support)))


def edit_message_text(message: Message, text: str, *args, **kwargs):
    return bot.edit_message_text(text, message.chat.id, message.id, *args, **kwargs)


@bot.callback_query_handler(func=lambda msg: msg.data is not None)
def callback_query_handler(callback: CallbackQuery):
    message = callback.message
    data = callback.data
    bot.clear_reply_handlers(message)

    if data == "self_add_balance":
        edit_message_text(message, "Send the amount of balance you want to add to your account",
                          reply_markup=cancel_kb)
        bot.register_next_step_handler(message, self_add_balance)

    elif data.startswith("social:"):
        social = data.split(":")[1]
        kb = InlineKeyboardMarkup()
        kb.add(*[InlineKeyboardButton(i,
               callback_data=f"order:{i}:100:{social}") for i in socials[social]])
        kb.add(InlineKeyboardButton("Back", callback_data="back_socials"))
        bot.send_photo(message.chat.id, open(f"images/{social.lower().replace(' ', '')}.{'png' if not social.lower() in ['tiktok', 'snapchat'] else 'jpg'}", "rb"),
                       f"Select the type of report you want to generate for {social}\n\n<i>$0.25 per report</i>", reply_markup=kb)

    elif data.startswith("order:") or data.startswith("plus:") or data.startswith("minus:"):
        report_type, value, social = data.split(":")[1:]
        value = int(value)
        if value < 100:
            bot.answer_callback_query(
                message.id, "Minimum amount is 100", show_alert=True)
            return
        kb = InlineKeyboardMarkup()
        plus = InlineKeyboardButton(
            "+", callback_data=f"plus:{report_type}:{value+10}:{social}")
        minus = InlineKeyboardButton(
            "-", callback_data=f"minus:{report_type}:{value-10}:{social}")
        num = InlineKeyboardButton(str(value), callback_data="String")
        kb.add(plus, num, minus)
        kb.add(InlineKeyboardButton(
            "Proceed", callback_data=f"proceed:{report_type}:{value}:{social}"))
        bot.edit_message_caption("How many reports do you want to generate",
                                 message.chat.id, message.id, reply_markup=kb)

    elif data.startswith("proceed:"):
        data = data.replace("proceed:", "")
        bot.send_message(
            message.chat.id, "Please select the violation in which the account being targeted best falls under.", reply_markup=report_kb(data))

    elif data.startswith("violation:"):
        social = data.split(":")[-1]
        bot.edit_message_text(
            f"Send the link to the {social} account you want to generate reports for", message.chat.id, message.id, reply_markup=cancel_kb)
        bot.register_next_step_handler(
            message, proceed_to_get_details, *data.split(":")[1:])

    elif data.startswith("pay:"):
        report_type, value, social, link, violation = data.split(":")[1:]
        user = get_user(message.chat.id)
        price = 0.25*int(value)
        if user.balance < price:
            bot.send_message(message.chat.id, f"Your balance is not enough to generate {value} reports. Click the button below to top up",
                             reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("💵Top up", callback_data="self_add_balance")))
            return
        user.balance -= price
        session.add(Order(user=user.id, value=value,
                    report_type=report_type, social_media=social, link=link))
        session.commit()
        bot.edit_message_text(
            f"Generating {value} {report_type} reports for {link}  on {social} because of violation of {report_violations[violation]}.\n\n<i>This may take up to 48 hours</i>", message.chat.id, message.id)
        for i in owners:
            bot.send_message(
                i, f"New order\n\nUser: <code>{message.chat.id}</code>\nSocial: {social}\nReport Type: {report_type}\nViolation: {report_violations[violation]}\nReports: {value}\nLink: {link}")

    elif data == "cancel":
        edit_message_text(message, "Operation Cancelled!")

    if data.startswith("admin_") and message.chat.id in owners:
        data = data[6:]

        if data == "home":
            bot.edit_message_text("<b>Hello Admin !</b> What do you want to edit?",
                                  message.chat.id, message.id, reply_markup=Admin.kb)

        elif data in ["pending_orders", "shipped_orders"]:
            pending_orders = session.query(Order).filter_by(
                shipped=data != "pending_orders").all()
            kb = InlineKeyboardMarkup()
            kb.add(*[InlineKeyboardButton(order.user,
                   callback_data=f"admin_order_details:{order.id}") for order in pending_orders])
            kb.add(Admin.back_btn("view_orders"))
            if data == "pending_orders":
                bot.edit_message_text(
                    "Pending orders", message.chat.id, message.id, reply_markup=kb)
            else:
                bot.edit_message_text(
                    "Shipped Orders", message.chat.id, message.id, reply_markup=kb)

        elif data.startswith("del_order"):
            _, orderid = data.split(":")
            order = session.query(Order).get(orderid)
            if not order:
                bot.answer_callback_query(
                    message.id, "This order has been deleted", show_alert=True)
                return
            for i in order.products:
                session.delete(i)
            session.delete(order)
            session.commit()
            bot.edit_message_text("Order deleted", message.chat.id, message.id,
                                  reply_markup=InlineKeyboardMarkup().add(Admin.back_btn("pending_orders")))

        elif data.startswith("order_details"):
            _, orderid = data.split(":")
            order_details = session.query(Order).get(orderid)
            if not order_details:
                bot.answer_callback_query(
                    message.id, "This order has been deleted", show_alert=True)
                return
            products = ""
            for i in order_details.products:
                products += f"<b>{i.name}</b>\n"
            kb = InlineKeyboardMarkup()
            if not order_details.shipped:
                kb.add(InlineKeyboardButton("🚚Mark as delivered",
                                            callback_data="admin_mark_shipped:" + str(orderid)))
                kb.add(InlineKeyboardButton("🗑Delete Order",
                       callback_data="admin_del_order:" + str(orderid)))
            kb.add(Admin.back_btn("pending_orders")
                   if not order_details.shipped else Admin.back_btn("shipped_orders"))
            bot.edit_message_text(
                f"User: {order_details.user}\nShipping: {'Delivered✅' if order_details.shipped else 'Pending⌛'}",
                message.chat.id,
                message.id, reply_markup=kb)

        elif data.startswith("mark_shipped"):
            _, orderid = data.split(":")
            order = session.query(Order).get(orderid)
            order.shipped = True
            session.commit()
            bot.edit_message_text("Order marked as delivered ✅", message.chat.id, message.id,
                                  reply_markup=InlineKeyboardMarkup().add(Admin.back_btn("pending_orders")))


def self_add_balance(message):
    if is_cancel(message):
        return
    try:
        amount = int(message.text)
    except ValueError:
        bot.send_message(
            message.chat.id, "Send the amount as a number (e.g 100, 200)", reply_markup=cancel_kb)
        bot.register_next_step_handler(message, self_add_balance)
        return
    if amount < 4:
        bot.send_message(
            message.chat.id, "Minimum amount is $4. Try again!", reply_markup=cancel_kb)
        bot.register_next_step_handler(message, self_add_balance)
        return
    res = sellix.create_payment(title="Add Balance", value=amount, currency="USD",
                                webhook=WEBHOOK_URL + "/paid", confirmations=10,
                                custom_fields={"telegram_id": message.chat.id}, email=admin_sellix_email, white_label=False, return_url="https://t.me/"+bot_username)
    bot.send_message(message.chat.id, f"Deposit ${amount}", reply_markup=InlineKeyboardMarkup().add(
        InlineKeyboardButton(f"💵Pay ${amount}", web_app=WebAppInfo(res["url"]))))


def is_cancel(message):
    if message.text in ["/start", "/admin", "/cancel"]:
        bot.clear_step_handler(message)
        bot.send_message(message.chat.id, "Operation cancelled")
        if message.text != "/cancel":
            globals()[message.text[1:]](message)
        return True
    return False


def proceed_to_get_details(message, violation, report_type, value, social):
    if is_cancel(message):
        return
    link = message.text
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        "Confirm", callback_data=f"pay:{report_type}:{value}:{social}:{link}:{violation}"))
    kb.add(InlineKeyboardButton("Cancel", callback_data="cancel"))
    bot.send_message(message.chat.id, f"<b>Confirm your order</b>\n\n{social}: {report_type}\nViolation: {report_violations[violation]}\nReports: {report_type}\nLink: {link}"
                     f"\n\n<i>Price: ${0.25*int(value)}\n$0.25 per report</i>", reply_markup=kb)


print("Started")
bot.infinity_polling()

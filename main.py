import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, BotCommand
from flask import Flask
from threading import Thread
import uuid
import logging
from datetime import datetime

# شناسه ادمین
ADMIN_ID = 6410680572  # شناسه‌ی تلگرام شما

# توکن رباتت
TOKEN = "7789250343:AAH1Pe07C9vavUXnofpmmzDsRmqp977CeIk"  # توکن جدید شما
bot = telebot.TeleBot(TOKEN)

# سرور Flask برای نگه داشتن ربات فعال
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080, debug=False)

def keep_alive():
    server_thread = Thread(target=run, daemon=True)
    server_thread.start()

# تنظیم لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# دیکشنری‌ها برای ذخیره سفارشات و موجودی
user_orders = {}  # سفارشات کاربران
pending_payments = {}  # پرداخت‌های در انتظار تأیید
user_entry_type = {}  # نوع ورود (برای آینده)

# محصولات و قیمت‌ها (کشمش و محصولات خاص)
products = {
    "keshmesh": {"name": "کشمش", "price": 600000, "stock": 50},  # قیمت کشمش 600,000 تومان
    "raki": {"name": "راکی (1 لیتر)", "price": 3500000, "stock": 1, "delivery_days": 30},
    "banana": {"name": "موز (1 لیتر)", "price": 2500000, "stock": 1, "delivery_days": 30},
    "apple": {"name": "سیب (1 لیتر)", "price": 2500000, "stock": 1, "delivery_days": 30},
    "liquor_orange": {"name": "لیکور پرتقال (1 لیتر)", "price": 800000, "stock": 1, "delivery_days": 30},
    "liquor_cherry": {"name": "لیکور آلبالو (1 لیتر)", "price": 800000, "stock": 1, "delivery_days": 30},
    "liquor_pineapple": {"name": "لیکور آناناس (1 لیتر)", "price": 800000, "stock": 1, "delivery_days": 30},
}

# توضیحات محصولات
product_descriptions = {
    "raki": {
        "description": (
            "🌟 **راکی (1 لیتر)** 🌟\n\n"
            "راکی یه نوشیدنی سنتی و معطر با طعم خاص انیسونه که از تقطیر انگور و افزودن دانه‌های انیسون به دست میاد. این نوشیدنی توی آب سرد یا با یخ سرو می‌شه و رنگش به سفید شیری تغییر می‌کنه، به همین خاطر بهش 'شیر اَسد' هم می‌گن! 🦁\n"
            "یه انتخاب عالی برای مهمونی‌ها و دورهمی‌های شماست. 😍"
        ),
        "image": "raki_image.jpg"
    },
    "banana": {
        "description": (
            "🍌 **ودکای موز (1 لیتر)** 🍌\n\n"
            "ودکای موز یه نوشیدنی خاص و خوش‌طعمه که با ترکیب ودکای خالص و عصاره‌ی طبیعی موز درست می‌شه. طعم شیرین و ملایم موز توی این نوشیدنی حس تازگی و لذت رو بهتون هدیه می‌ده. 🍹\n"
            "بهترین انتخاب برای کسایی که دنبال یه طعم جدید و متفاوتن! ✨"
        ),
        "image": "banana_image.jpg"
    },
    "apple": {
        "description": (
            "🍎 **ودکای سیب (1 لیتر)** 🍎\n\n"
            "ودکای سیب با عصاره‌ی سیب‌های تازه و ودکای باکیفیت درست می‌شه. طعم ترد و ترش‌وشیرین سیب توی این نوشیدنی حس طراوت و شادابی رو بهتون می‌ده. 🍏\n"
            "یه نوشیدنی عالی برای کسایی که عاشق طعم‌های میوه‌ای هستن! 🌟"
        ),
        "image": "apple_image.jpg"
    },
    "liquor_orange": {
        "description": (
            "🍊 **لیکور پرتقال (1 لیتر)** 🍊\n\n"
            "لیکور پرتقال از پوست پرتقال‌های تازه و شیرین به همراه الکل خالص درست می‌شه. طعم شیرین و مرکباتی این لیکور باعث می‌شه که هم به‌تنهایی و هم توی کوکتل‌ها عالی باشه. 🍹\n"
            "یه انتخاب فوق‌العاده برای کسایی که عاشق طعم‌های ترش و شیرینن! ✨"
        ),
        "image": "liquor_orange_image.jpg"
    },
    "liquor_cherry": {
        "description": (
            "🍒 **لیکور آلبالو (1 لیتر)** 🍒\n\n"
            "لیکور آلبالو با استفاده از آلبالوهای تازه و رسیده درست می‌شه که طعم ترش و شیرینش حس نوستالژی رو زنده می‌کنه. این نوشیدنی با الکل ملایم و طعم غلیظ آلبالو، یه انتخاب عالی برای دورهمی‌هاست. 🥂\n"
            "یه طعم کلاسیک که نمی‌تونی ازش بگذری! 😋"
        ),
        "image": "liquor_cherry_image.jpg"
    },
    "liquor_pineapple": {
        "description": (
            "🍍 **لیکور آناناس (1 لیتر)** 🍍\n\n"
            "لیکور آناناس با عصاره‌ی آناناس‌های استوایی و شیرین درست می‌شه. طعم شیرین و گرمسیری این نوشیدنی حس یه تعطیلات ساحلی رو بهتون می‌ده. 🏝️\n"
            "یه نوشیدنی شاد و پرانرژی برای کسایی که دنبال طعم‌های خاصن! 🌺"
        ),
        "image": "liquor_pineapple_image.jpg"
    }
}

# تابع برای تبدیل اعداد فارسی به انگلیسی
def convert_persian_to_english(text):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    translation_table = str.maketrans(persian_digits, english_digits)
    return text.translate(translation_table)

# تنظیم منوی همیشگی
def set_persistent_menu():
    commands = [
        BotCommand("start", "🔄 شروع مجدد"),
        BotCommand("menu", "📜 نمایش منو"),
        BotCommand("checkout", "💳 مشاهده فاکتور"),
        BotCommand("edit", "📝 ویرایش فاکتور")
    ]
    bot.set_my_commands(commands)

# دکمه بازگشت به منو
def back_to_menu():
    markup = InlineKeyboardMarkup()
    btn_back = InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu")
    markup.add(btn_back)
    return markup

# دکمه ارسال فیش
def send_receipt_button():
    markup = InlineKeyboardMarkup()
    btn_send = InlineKeyboardButton("📤 ارسال فیش", callback_data="send_receipt")
    markup.add(btn_send)
    return markup

# منوی اصلی
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("🛍 نمایش محصولات", callback_data="show_products")
    btn2 = InlineKeyboardButton("📦 سفارش محصول خاص", callback_data="order_specific")
    btn3 = InlineKeyboardButton("📝 ویرایش سفارش", callback_data="edit_order")
    btn4 = InlineKeyboardButton("💳 نهایی کردن سفارش", callback_data="finalize_order")
    btn5 = InlineKeyboardButton("📖 توضیحات محصولات", callback_data="show_descriptions")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# منوی محصولات
def products_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    for product_id, product in products.items():
        if product_id not in ["raki", "banana", "apple", "liquor_orange", "liquor_cherry", "liquor_pineapple"]:  # محصولات خاص رو اینجا نشون نمی‌دیم
            markup.add(InlineKeyboardButton(f"🌿 {product['name']} - {product['price']:,} تومان (موجودی انبار: {product['stock']})", callback_data=f"select_{product_id}"))
    markup.add(InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu"))
    return markup

# منوی سفارش محصول خاص
def specific_products_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    for product_id, product in products.items():
        if product_id in ["raki", "banana", "apple", "liquor_orange", "liquor_cherry", "liquor_pineapple"]:  # محصولات خاص
            markup.add(InlineKeyboardButton(f"🌿 {product['name']} - {product['price']:,} تومان (موجودی انبار: {product['stock']})", callback_data=f"select_{product_id}"))
    markup.add(InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu"))
    return markup

# منوی توضیحات محصولات
def descriptions_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    for product_id in product_descriptions.keys():
        markup.add(InlineKeyboardButton(f"📖 {products[product_id]['name']}", callback_data=f"desc_{product_id}"))
    markup.add(InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu"))
    return markup

# خوش‌آمدگویی با عکس
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_orders[chat_id] = {}  # مقداردهی اولیه برای سفارشات کاربر
    user_entry_type[chat_id] = None
    first_name = message.from_user.first_name or "دوست عزیز"
    welcome_caption = (
        f"سلام {first_name} جان 😍\n"
        "به ربات فروش نوشیدنی خوش اومدی! 🌿\n"
        "اینجا می‌تونی عرقیجات طبیعی و باکیفیت سفارش بدی. 🛒\n"
        "با چند کلیک ساده سفارش بده و لذت ببر!و برو جایی که غم نباشه. 😊"
    )
    set_persistent_menu()
    try:
        with open("welcome_image.jpg", "rb") as photo:
            bot.send_photo(chat_id, photo, caption=welcome_caption, reply_markup=main_menu())
    except FileNotFoundError:
        bot.send_message(chat_id, welcome_caption, reply_markup=main_menu())
        logging.warning("عکس welcome_image.jpg پیدا نشد!")

# نمایش منو
@bot.message_handler(commands=['menu'])
def show_menu(message):
    bot.send_message(message.chat.id, "📜 منوی اصلی:", reply_markup=main_menu())

# مشاهده فاکتور
@bot.message_handler(commands=['checkout'])
def checkout_command(message):
    show_invoice(message.chat.id)

# ویرایش فاکتور
@bot.message_handler(commands=['edit'])
def edit_command(message):
    edit_order(message.chat.id)

# محاسبه کل مبلغ
def calculate_total(chat_id):
    if chat_id not in user_orders or not user_orders[chat_id]:
        return 0
    total = sum(products[item]["price"] * count for item, count in user_orders[chat_id].items())
    return total

# نمایش فاکتور
def show_invoice(chat_id):
    if chat_id not in user_orders or not user_orders[chat_id]:
        bot.send_message(chat_id, "⛔ سفارشی ثبت نشده!", reply_markup=main_menu())
        return
    total = calculate_total(chat_id)
    items_list = "\n".join([f"{products[item]['name']} ({count} عدد) - {products[item]['price'] * count:,} تومان" for item, count in user_orders[chat_id].items()])
    invoice_text = (
        f"📝 سفارش شما:\n"
        f"{items_list}\n\n"
        f"💰 مجموع پرداختی: {total:,} تومان\n\n\n"
        f"<b>عزیزان لطفا بعد از پرداخت کارت به کارت عکس فیش رو همینجا ارسال کنید 😎 ممنون از شما😊</b>\n\n\n"
        f"💳 مبلغ را به کارت <code>5022291073692012</code> جواد رنجبر واریز کنید."
    )
    bot.send_message(chat_id, invoice_text, reply_markup=send_receipt_button(), parse_mode="HTML")

# ویرایش سفارش
def edit_order(chat_id):
    logging.info(f"تابع edit_order برای chat_id={chat_id} اجرا شد.")
    if chat_id not in user_orders or not user_orders[chat_id]:
        bot.send_message(chat_id, "⛔ سفارشی ثبت نشده!", reply_markup=main_menu())
        logging.info(f"سفارشی برای chat_id={chat_id} ثبت نشده.")
        return
    markup = InlineKeyboardMarkup()
    for item, count in user_orders[chat_id].items():
        button_text = f"❌ حذف {products[item]['name']} ({count} عدد)"
        callback_data = f"remove_{item}"
        markup.add(InlineKeyboardButton(button_text, callback_data=callback_data))
        logging.info(f"دکمه حذف برای آیتم {item} با callback_data={callback_data} اضافه شد.")
    markup.add(InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_menu"))
    bot.send_message(chat_id, "📝 موارد قابل حذف:", reply_markup=markup)
    logging.info(f"پیام 'موارد قابل حذف' برای chat_id={chat_id} ارسال شد.")

# حذف آیتم
def remove_item(call):
    chat_id = call.message.chat.id
    logging.info(f"تابع remove_item برای chat_id={chat_id} اجرا شد. call.data={call.data}")
    
    # استخراج نام آیتم
    item = call.data.split("_", 1)[1]
    logging.info(f"آیتم استخراج‌شده: {item}")
    
    # بررسی وجود آیتم در سفارشات
    if item in user_orders[chat_id]:
        logging.info(f"آیتم {item} در user_orders[{chat_id}] پیدا شد. در حال حذف...")
        del user_orders[chat_id][item]  # حذف آیتم از سفارشات
        bot.answer_callback_query(call.id, f"❌ {products[item]['name']} حذف شد.")
        logging.info(f"آیتم {item} با موفقیت حذف شد.")
    else:
        bot.answer_callback_query(call.id, "⚠️ آیتم یافت نشد!")
        logging.warning(f"آیتم {item} در user_orders[{chat_id}] پیدا نشد.")
        return
    
    # حذف پیام قبلی
    bot.delete_message(chat_id, call.message.message_id)
    logging.info(f"پیام قبلی با message_id={call.message.message_id} حذف شد.")
    
    # ارسال پیام جدید با سفارشات باقی‌مونده
    if user_orders[chat_id]:
        markup = InlineKeyboardMarkup()
        for remaining_item, remaining_count in user_orders[chat_id].items():
            markup.add(InlineKeyboardButton(f"❌ حذف {products[remaining_item]['name']} ({remaining_count} عدد)", callback_data=f"remove_{remaining_item}"))
        markup.add(InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_menu"))
        bot.send_message(chat_id, "📝 موارد باقی‌مونده:", reply_markup=markup)
        logging.info(f"پیام 'موارد باقی‌مونده' برای chat_id={chat_id} ارسال شد.")
    else:
        bot.send_message(chat_id, "⛔ همه سفارشات حذف شدند!", reply_markup=back_to_menu())
        logging.info(f"پیام 'همه سفارشات حذف شدند' برای chat_id={chat_id} ارسال شد.")

# مدیریت دکمه‌ها
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    logging.info(f"دکمه زده شد: call.data={call.data}")
    try:
        if call.data == "show_products":
            bot.send_message(chat_id, "🌿 محصولات موجود:\nلطفاً محصول مورد نظرت رو انتخاب کن:", reply_markup=products_menu())
        elif call.data == "order_specific":
            bot.send_message(chat_id, "📦 سفارش محصول خاص:\n⚠️ توجه: محصولات خاص 30 روز پس از ثبت سفارش به دست شما می‌رسد.\n👇 گزینه‌ها رو انتخاب کن:", reply_markup=specific_products_menu())
        elif call.data == "edit_order":
            edit_order(chat_id)
        elif call.data == "finalize_order":
            show_invoice(chat_id)
        elif call.data == "back_to_menu":
            bot.send_message(chat_id, "📜 منوی اصلی:", reply_markup=main_menu())
        elif call.data == "show_descriptions":
            bot.send_message(chat_id, "📖 توضیحات محصولات:\nلطفاً محصول مورد نظرت رو انتخاب کن:", reply_markup=descriptions_menu())
        elif call.data.startswith("desc_"):
            product_id = call.data.split("_")[1]
            description = product_descriptions[product_id]["description"]
            image_path = product_descriptions[product_id]["image"]
            try:
                with open(image_path, "rb") as photo:
                    bot.send_photo(chat_id, photo, caption=description, reply_markup=back_to_menu(), parse_mode="HTML")
            except FileNotFoundError:
                bot.send_message(chat_id, description, reply_markup=back_to_menu(), parse_mode="HTML")
                logging.warning(f"عکس {image_path} پیدا نشد!")
        elif call.data.startswith("select_"):
            product_id = call.data.split("_")[1]
            product = products[product_id]
            bot.send_message(chat_id, f"🌿 {product['name']} - موجودی: {product['stock']}\nلطفاً تعداد مورد نظرت رو به صورت عدد وارد کن (مثلاً 10):", reply_markup=ReplyKeyboardRemove())
            bot.register_next_step_handler(call.message, lambda msg: handle_quantity(msg, product_id))
        elif call.data == "send_receipt":
            bot.send_message(chat_id, "📤 لطفا عکس فیش رو بفرست همینجا و منتظر بمون 😎")
        elif call.data.startswith("remove_"):
            logging.info(f"دکمه حذف شناسایی شد: call.data={call.data}")
            remove_item(call)
        elif call.data.startswith("approve_") or call.data.startswith("reject_"):
            admin_id = call.message.chat.id
            if admin_id != ADMIN_ID:
                bot.answer_callback_query(call.id, "⛔ شما اجازه ندارید!")
                return
            payment_id = call.data.split("_")[1]
            if payment_id not in pending_payments:
                bot.answer_callback_query(call.id, "⛔ اطلاعات پرداخت یافت نشد!")
                return
            payment_info = pending_payments.pop(payment_id)
            user_id = payment_info["user_id"]
            username = payment_info["username"]
            total = payment_info["total"]
            items_list = payment_info["items"]
            # به‌روزرسانی موجودی انبار بعد از تأیید
            for item, count in payment_info["order_details"].items():
                products[item]["stock"] -= count  # کم کردن از موجودی
            if call.data.startswith("approve_"):
                bot.send_message(user_id, "✅ واریزی شما تأیید شد. بزودی تماس می‌گیریم.")
                bot.send_message(ADMIN_ID, f"✅ پرداخت {username} تأیید شد.")
                bot.answer_callback_query(call.id, "✅ پرداخت تأیید شد!")
            else:
                bot.send_message(user_id, "❌ پرداخت رد شد. با پشتیبانی تماس بگیرید.")
                bot.send_message(ADMIN_ID, f"❌ پرداخت {username} رد شد.")
                bot.answer_callback_query(call.id, "❌ پرداخت رد شد!")
            bot.edit_message_reply_markup(ADMIN_ID, call.message.message_id, reply_markup=None)
        else:
            logging.warning(f"دکمه ناشناخته: call.data={call.data}")
    except Exception as e:
        logging.error(f"خطا در callback_query: {e}")
        bot.send_message(chat_id, "⚠️ مشکل پیش اومد، دوباره امتحان کن!")

# مدیریت تعداد انتخاب‌شده
def handle_quantity(message, product_id):
    chat_id = message.chat.id
    text = message.text
    product = products[product_id]

    if text == "لغو":
        bot.send_message(chat_id, "❌ سفارش لغو شد.", reply_markup=main_menu())
        return

    # تبدیل اعداد فارسی به انگلیسی
    text = convert_persian_to_english(text)

    try:
        quantity = int(text)
        if quantity <= 0:
            bot.send_message(chat_id, "⚠️ تعداد باید بیشتر از 0 باشه!", reply_markup=main_menu())
            return
        if quantity > product["stock"]:
            bot.send_message(chat_id, f"⚠️ موجودی کافی نیست! فقط {product['stock']} عدد موجوده.", reply_markup=main_menu())
            return

        # اضافه کردن به سبد خرید
        if chat_id not in user_orders:
            user_orders[chat_id] = {}
        if product_id in user_orders[chat_id]:
            user_orders[chat_id][product_id] += quantity
        else:
            user_orders[chat_id][product_id] = quantity
        bot.send_message(chat_id, f"✅ {product['name']} ({quantity} عدد) به سبد خریدت اضافه شد.", reply_markup=main_menu())
    except ValueError:
        bot.send_message(chat_id, "⚠️ لطفاً یه عدد معتبر وارد کن!", reply_markup=main_menu())

# مدیریت فیش
@bot.message_handler(content_types=['photo'])
def handle_payment_receipt(message):
    chat_id = message.chat.id
    if chat_id not in user_orders or not user_orders[chat_id]:
        bot.send_message(chat_id, "⛔ سفارشی ثبت نشده!", reply_markup=back_to_menu())
        return
    payment_id = str(uuid.uuid4())[:8]
    total = calculate_total(chat_id)
    items_list = "\n".join([f"{products[item]['name']} ({count} عدد)" for item, count in user_orders[chat_id].items()])
    bot.send_message(chat_id, "✅ فیش دریافت شد، منتظر بررسی باشید.")
    pending_payments[payment_id] = {
        "user_id": chat_id,
        "username": message.from_user.first_name or "کاربر",
        "total": total,
        "items": items_list,
        "file_id": message.photo[-1].file_id,
        "order_details": user_orders[chat_id].copy()  # برای به‌روزرسانی موجودی بعد از تأیید
    }
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ تأیید", callback_data=f"approve_{payment_id}"))
    markup.add(InlineKeyboardButton("❌ رد", callback_data=f"reject_{payment_id}"))
    caption = (
        f"🆕 پرداخت جدید:\n"
        f"👤 کاربر: {message.from_user.first_name or 'کاربر'}\n"
        f"📝 سفارشات:\n{items_list}\n"
        f"💰 مبلغ: {total:,} تومان\n\n"
        "📌 بررسی کنید."
    )
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup)

# شروع سرور Flask و ربات
if __name__ == "__main__":
    keep_alive()  # فعال کردن سرور Flask برای جلوگیری از خوابیدن
    bot.polling(none_stop=True)

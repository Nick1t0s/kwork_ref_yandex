import os

import telebot
from telebot import types
import configparser
from database import *
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
config = configparser.ConfigParser()
config.read("config.ini")
token = os.getenv("token")
bot = telebot.TeleBot(token)

# Вспомогательные переменные, дальше не использовать
ru_ref = config["Telegram"]["ru_ref"]
uz_ref = config["Telegram"]["uz_ref"]
kz_ref = config["Telegram"]["kz_ref"]
kg_ref = config["Telegram"]["kg_ref"]
by_ref = config["Telegram"]["by_ref"]

ref_data = {"ru": ru_ref,
            "uz": uz_ref,
            "kz": kz_ref,
            "kg": kg_ref,
            "by": by_ref}
init_db()
def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc]) or url[0] == "~" #Это фича!!!!

def change_ref(message, country):
    if not is_valid_url(message.text):
        bot.send_message(message.chat.id,
                         "<b>❌Ссылка не является URL❌</b>",
                         parse_mode="HTML")
        start(message)
    else:
        config.set("Telegram", f"{country}_ref", message.text.strip("~"))
        with open("config.ini", "w", encoding="UTF-8") as f:
            config.write(f)
        ref_data[country] = message.text.strip("~")
        bot.send_message(message.chat.id,
                         "<b>Ссылка была успешно изменена</b>",
                         parse_mode="HTML")
        start(message)

def change_text(message, country):
    with open(f"data/{country}.txt", "w", encoding="UTF-8") as f:
        f.write(message.text)
    bot.send_message(message.chat.id,
                     "<b>Ссылка была успешно изменена</b>",
                     parse_mode="HTML")
    start(message)

@bot.message_handler(commands=["start"])
def start(message):
    print("xxx")
    if message.chat.id == int(config["Telegram"]["admin_id"]):
        total_clicks = get_total_clicks()
        today_clicks = get_today_clicks()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Изменить реф. ссылку", callback_data="change_ref"))
        markup.add(types.InlineKeyboardButton("Изменить текст сообщений", callback_data="change_text"))
        markup.add(types.InlineKeyboardButton("Очистить статистику", callback_data="clear"))

        bot.send_message(message.chat.id,
                         f"<b>Всего кликов: {total_clicks}\nСегодня кликов: {today_clicks}</b>",
                         reply_markup=markup,
                         parse_mode="HTML")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🇷🇺 Россия", callback_data="ru"))
        markup.add(types.InlineKeyboardButton("🇰🇬 Кыргызстан", callback_data="kg"))
        markup.add(types.InlineKeyboardButton("🇺🇿 Узбекистан", callback_data="uz"))
        markup.add(types.InlineKeyboardButton("🇧🇾 Беларусь", callback_data="by"))
        markup.add(types.InlineKeyboardButton("🇰🇿 Казахстан", callback_data="kz"))
        with open("data/start.jpg", "rb") as f:
            photo = f.read()
        bot.send_photo(message.chat.id, photo=photo,
                       caption="<b>В какой стране ты будешь работать?</b>",
                       reply_markup=markup, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "another_reg":
        bot.delete_message(call.message.chat.id, call.message.id)
        start(call.message)
    # elif call.data[:17] == "fast_registration":
    #     # Записываем в базу данных факт нажатия
    #     record_click(call.from_user.id)
    #     markup = types.InlineKeyboardMarkup()
    #     markup.add(types.InlineKeyboardButton("❌ Назад", callback_data="start"))
    #     # Перенаправляем пользователя по ссылке
    #     bot.send_message(call.message.chat.id,
    #                      f"<b><a href='{ref_data[call.data[17:]]}'>🎯 Перейти по ссылке</a></b>",
    #                      parse_mode="HTML",
    #                      reply_markup=markup)
    elif call.data == "change_ref":
        bot.delete_message(call.message.chat.id, call.message.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🇷🇺 Россия", callback_data="ru_change"))
        markup.add(types.InlineKeyboardButton("🇰🇬 Кыргызстан", callback_data="kg_change"))
        markup.add(types.InlineKeyboardButton("🇺🇿 Узбекистан", callback_data="uz_change"))
        markup.add(types.InlineKeyboardButton("🇧🇾 Беларусь", callback_data="by_change"))
        markup.add(types.InlineKeyboardButton("🇰🇿 Казахстан", callback_data="kz_change"))
        markup.add((types.InlineKeyboardButton("❌ Назад", callback_data="back_change")))
        bot.send_message(call.message.chat.id,
                         "<b>Выберите страну</b>",
                         reply_markup=markup,
                         parse_mode="HTML")
    elif call.data[call.data.find("_")+1:] == "change":
        country = call.data[:call.data.find("_")]
        if country == "back":
            bot.delete_message(call.message.chat.id, call.message.id)
            start(call.message)
        else:
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id,
                             "<b>Пришлите новую ссылку(используйте ~ в начале чтобы игнорировать проверку ссылки): </b>",
                             parse_mode="HTML")
            bot.register_next_step_handler(call.message, change_ref, country)

    elif call.data == "change_text":
        bot.delete_message(call.message.chat.id, call.message.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🇷🇺 Россия", callback_data="ru_change_t"))
        markup.add(types.InlineKeyboardButton("🇰🇬 Кыргызстан", callback_data="kg_change_t"))
        markup.add(types.InlineKeyboardButton("🇺🇿 Узбекистан", callback_data="uz_change_t"))
        markup.add(types.InlineKeyboardButton("🇧🇾 Беларусь", callback_data="by_change_t"))
        markup.add(types.InlineKeyboardButton("🇰🇿 Казахстан", callback_data="kz_change_t"))
        markup.add((types.InlineKeyboardButton("❌ Назад", callback_data="back_change")))

        bot.send_message(call.message.chat.id,
                         "<b>Выберите текст для редактирования: </b>",
                         parse_mode="HTML",
                         reply_markup=markup)

    elif call.data[-2:] == "_t":
        country = call.data[:call.data.find("_")]
        if country == "back":
            bot.delete_message(call.message.chat.id, call.message.id)
            start(call.message)
        else:
            bot.send_message(call.message.chat.id,
                             "<b>Пришлите новый текст: </b>",
                             parse_mode="HTML")
            bot.register_next_step_handler(call.message, change_text, country)

    elif call.data == "start":
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.delete_message(call.message.chat.id, call.message.id-1)
        start(call.message)

    elif call.data == "clear":
        print(1)
        clear()
        print(2)
        bot.delete_message(call.message.chat.id, call.message.id)
        start(call.message)
        print(3)

    else:
        print("else")
        with open(f"data/{call.data}.txt", "r", encoding="UTF-8") as f:
            text = f.read()
        with open("data/second.jpg", "rb") as f:
            photo = f.read()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "🚀 Быстрая регистрация", url=f"{config['Telegram']['my_ip']}?redirect={ref_data[call.data]}&id={call.message.chat.id}"))
        markup.add(types.InlineKeyboardButton("🤝 Позвать друга",
                                              url="https://t.me/share/url?url=https://t.me/yandexeda_reg_bot&text=👋🏼"))
        markup.add(types.InlineKeyboardButton("🌍 Работа в других регионах", callback_data="another_reg"))

        bot.delete_message(call.message.chat.id, call.message.id)
        print("fdsg")
        bot.send_photo(call.message.chat.id, photo=photo, caption=text, reply_markup=markup, parse_mode='HTML')


@bot.message_handler()  # TODO: проверить работу
def another_message(message):
    start(message)

while True:
    bot.polling(none_stop=True)
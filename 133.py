from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("VISUAL_CROSSING_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")

WEATHER_REPORT_FOR_CITIES = {
    "Kaliningrad": "Kaliningrad",
    "Moscow": "Moscow",
    "Kazan": "Kazan"
}

bot = TeleBot(TOKEN)
user_city = {}

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=3)
    for cityes in WEATHER_REPORT_FOR_CITIES.keys():
        item_button = KeyboardButton(cityes)
        markup.add(item_button)
    bot.send_message(message.chat.id, "Choose a city", reply_markup=markup)



@bot.message_handler(func=lambda message: message.text in WEATHER_REPORT_FOR_CITIES.keys())
def save_city(message):
    user_city[message.from_user.id] = message.text

    markup = ReplyKeyboardMarkup(row_width=1)
    markup.add(KeyboardButton("Выбрать дату"))
    bot.send_message(message.chat.id, "выбери дату за которую тебе нужна инфа", reply_markup=markup)





@bot.message_handler(func=lambda message: message.text == "Выбрать дату")
def ask_date(message):
    if message.from_user.id not in user_city:
        bot.send_message(message.chat.id, "Сначала выбери город!")
    else:
        bot.send_message(message.chat.id, "Напиши дату в формате ДАТА.МЕСЯЦ.ГОД (30.05.2027)")

@bot.message_handler(func=lambda message: True)
def check_date(message):
    user_id = message.from_user.id
    try:
        date = datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат. Напиши дату так: 20.03.2026")
        return

    city = user_city[user_id]
    date_str = date.strftime("%Y-%m-%d")
    hours = get_weather_by_hours_for_day_from_api(date=date_str, city=city)
    result = format_weather(hours, city, message.text)
    bot.send_message(message.chat.id, result)

def format_weather(hours, city, text):
    lines = [f"Погода в {city} на {text}:\n"]
    for hour in hours[::3]:
        time = hour["datetime"][:5]
        temp_c = round((hour["temp"] - 32) * 5 / 9)
        conditions = hour["conditions"]
        lines.append(f"{time} -  {temp_c}°C, {conditions}")
    return "\n".join(lines)

def get_weather_by_hours_for_day_from_api(*, date: str, city: str) -> list[dict]:
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{date}/{date}?unitGroup=us&key={API_KEY}"
    response = requests.get(url)
    weather_by_days = response.json()["days"]
    weather_by_hours = weather_by_days[0]["hours"]
    return weather_by_hours

bot.infinity_polling()

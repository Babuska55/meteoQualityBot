import telebot 
import requests
from flask import Flask, request
import os
import json
from datetime import datetime   
from collections import defaultdict

bot=telebot.TeleBot("7863228849:AAFU3bwjvTYPfKgHa1Ihapuyj0hzQUbzGgk")
API='937ac758fd88de28beb4c24fbdc2fa63'


app = Flask(__name__)

def weather_icon(desc):
    desc = desc.lower()
    if "ясно" in desc:
        return "☀️"
    elif "облачно" in desc:
        return "☁️"
    elif "пасмурно" in desc:
        return "🌥"
    elif "дождь" in desc:
        return "🌧" if "небольшой" not in desc else "🌦"
    elif "снег" in desc:
        return "❄️"
    elif "туман" in desc:
        return "🌫"
    else:
        return ""

@bot.message_handler(commands=['start'])

def start(message):
    bot.send_message(message.chat.id, 'Привет! 👋 Добро пожаловать! 🌟 Напиши название города, чтобы получить актуальные новости о погоде 🌤️.')


@bot.message_handler(content_types=['text'])
def get_weather(message):
    city=message.text.strip().lower()

    res=requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')

    if res.status_code==200:
        data=json.loads(res.text)
        temp=data["main"]["temp"]
        bot.reply_to(message, f'Сейчас погода:{temp}°C')
        
        # Картинка
        def get_image_file(description):
            description = description.lower()

            if "clear" in description or "sky" in description:
                return 'summer.png'
            elif "rain" in description:
                return 'rain.png'
            elif "cloud" in description:
                return 'cloud.png'
            elif "snow" in description:
                return 'snow.png'
            elif "fog" in description:
                return 'fog.png'
            else:
                return None  # if no match found
            
        # Используем описание погоды для выбора изображения
        desc = data["weather"][0]["description"]
        image = get_image_file(desc)
        if image:
            with open('./' + image, 'rb') as file:
                bot.send_photo(message.chat.id, file)
        else:
            bot.send_message(message.chat.id, "Не удалось найти фотку!")

        forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric&lang=ru'
        forecast_res = requests.get(forecast_url)

        if forecast_res.status_code == 200:
            data2 = forecast_res.json()
            forecast_list = data2["list"] 
            forecast_by_day = defaultdict(list)

            # Собираем прогноз по дням
            for item in forecast_list:
                dt_txt=item['dt_txt'] # формат "2025-03-23 15:00:00"
                date=dt_txt.split()[0]
                time=dt_txt.split()[1]
                temp = item["main"]["temp"]
                desc = item['weather'][0]['description']
                forecast_by_day[date].append((time, temp, desc))

            # Формирование ответа
            reply = f'🌤 Прогноз погоды в городе {city.title()}:\n\n'
            days = list(forecast_by_day.keys())[:3]  # первые 3 дня

                
                
            for date in days: 
                pretty_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")
                reply += f'📅 {pretty_date}:\n'
                for time, temp, desc in forecast_by_day[date]:
                    if time in ['09:00:00', '12:00:00', '15:00:00', '18:00:00','21:00:00']:
                        icon = weather_icon(desc)
                        reply += f'🕒 {time[:-3]} — {temp:.1f}°C, {icon} {desc}\n'
                reply += '\n'
                
            bot.send_message(message.chat.id, reply)
        else:
              bot.send_message(message.chat.id, "Ошибка при получении прогноза.")        
    else:   
        bot.reply_to(message, f'Город написан не верно.')
  
#bot.polling(none_stop=True)

@app.route('/' + API, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# Главная страница для теста
@app.route('/')
def index():
    return "Hello World!", 200

if __name__ == '__main__':
    # Убираем polling() и настраиваем вебхук
    bot.remove_webhook()
    bot.set_webhook(url=f'https://meteoqualitybot.onrender.com/{API}')

    
    # Используем PORT из переменных окружения Render или указываем дефолтный порт 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
import telebot 
import requests
import json
from datetime import datetime   
from collections import defaultdict

bot=telebot.TeleBot("7863228849:AAFU3bwjvTYPfKgHa1Ihapuyj0hzQUbzGgk")
API='937ac758fd88de28beb4c24fbdc2fa63'

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
    bot.send_message(message.chat.id,'Привет новый пользователь, напииши название города!')

@bot.message_handler(content_types=['text'])
def get_weather(message):
    city=message.text.strip().lower()

    res=requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')

    if res.status_code==200:
        data=json.loads(res.text)
        temp=data["main"]["temp"]
        bot.reply_to(message, f'Сейчас погода:{temp}°C')

        # Картинка
        def get_image_filename(description):
            description = description.lower()
            if "ясно" in description or "clear" in description:
                return "summer.png"
            elif "дождь" in description or "rain" in description:
                return "rain.png"
            elif "облачно" in description or "cloud" in description:
                return "cloud.png"
            elif "снег" in description or "snow" in description:
                return "snow.png"
            elif "туман" in description or "fog" in description:
                return "fog.png"
            else:
                return "default.png"

        # Потом используем
        desc = data["weather"][0]["description"]
        image = get_image_filename(desc)

        try:
            file = open(f'C:\\Users\\User\\Desktop\\ChatBots\\MeteoQuality\\{image}', 'rb')
            bot.send_photo(message.chat.id, file)
        except FileNotFoundError:
            bot.send_message(message.chat.id, "Картинка не найдена.")
        
       

        
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
  
bot.polling(none_stop=True)

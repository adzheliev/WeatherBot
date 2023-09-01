"""Main bot module"""
import datetime
import requests
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from config import bot_token, weather_token

bot = Bot(token=bot_token)
dispatcher = Dispatcher(bot)


@dispatcher.message_handler(commands=['start'])
async def start_command(message: types.Message):
    """Function generates welcome message at the start command"""
    await message.reply('Добрый день! Напишите название города, '
                        'в котором Вы бы хотели узнать погоду')


@dispatcher.message_handler()
async def get_weather(message: types.Message):
    """Function recieves cityname and returns weather report"""
    try:
        r = requests.get(
            f'http://api.openweathermap.org/geo/1.0/direct?q={message.text}'
            f'&appid={weather_token}')
        data = r.json()
    except ValueError:
        await message.reply('Проверьте название города')

    lat = data[0]['lat']
    lon = data[0]['lon']

    try:
        r = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?'
            f'lat={lat}&lon={lon}'
            f'&appid={weather_token}&units=metric&lang=ru'
        )
        data_ = r.json()

        city = data_['name']
        current_temperature = data_['main']['temp']
        weather_type = data_['weather'][0]['description']
        temperature_feels_like = data_['main']['feels_like']
        humidity = data_['main']['humidity']
        pressure = data_['main']['pressure']
        wind_speed = data_['wind']['speed']
        sunrise_time = datetime.datetime.fromtimestamp(data_['sys']['sunrise'])
        sunset_time = datetime.datetime.fromtimestamp(data_['sys']['sunset'])
        day_len = sunset_time - sunrise_time

        await message.reply(
            f'Сегодня {datetime.datetime.now().strftime("%d.%m.%Yг. %H:%M")}\n'
            f'Погода в городе {city}\n'
            f'Температура {current_temperature} C°, '
            f'ощущается как {temperature_feels_like} C° '
            f'- {weather_type}\n'
            f'Относительная влажность воздуха {humidity}%\n'
            f'Атмосферное давление {pressure} мм.рт.ст\n'
            f'Скорость ветра {wind_speed} м/с\n'
            f'Время рассвета {sunrise_time.hour}:{sunrise_time.minute}\n'
            f'Время захода солнца {sunset_time.hour}:{sunset_time.minute}\n'
            f'Продолжительность светового дня {day_len}'
        )
    except ConnectionError:
        await message.reply(
            'Возникла проблема со связью! Проверьте соединение!'
        )


if __name__ == '__main__':
    executor.start_polling(dispatcher)

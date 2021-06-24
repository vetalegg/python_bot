import aiogram
from aiogram.utils import exceptions
from aiogram import Bot, types, utils
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests
import json
from bs4 import BeautifulSoup
import random

button_currency = KeyboardButton('Курс валют')
button_news = KeyboardButton('Случайная новость с панорамы')
button_covid = KeyboardButton('Статистика COVID19 в Москве')
button_coin = KeyboardButton('Подбросить монетку')
button_help = KeyboardButton('Помощь')

mainWindowKb = ReplyKeyboardMarkup(resize_keyboard=True)
mainWindowKb.add(button_currency).row(button_news).row(button_covid).row(button_coin).row(button_help)

API_TOKEN = '1895740117:AAFTC3TFG1UdzOytWvnLyQPl7Y3kVYnQeEk'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def start_process(message: types.Message):
    await bot.send_message(message.from_user.id, 'Привет! Я бот, который умеет:\n'
                                                 '■Рассказать о курсе валют\n'
                                                 '■Выдать случайную юмористическую новость ИА "Панорама"\n'
                                                 '■Представить статистику заболеваемости COVID-19 в Москве\n'
                                                 '■Подбросить монетку для принятия сложных решений ',
                           reply_markup=mainWindowKb)


@dp.message_handler(lambda message: message.text == "Статистика COVID19 в Москве")
async def info_message(message: types.Message):
    response = requests.get('https://yastat.net/s3/milab/2020/covid19-stat/data/v10/data-by-region/213.json').json()["info"]
    formed_str = f'Население Москвы: {response["population"]}\n' \
                f'Выявлено заражений: {response["cases"]}\n' \
                f'Заражений за пследние сутки: {response["cases_delta"]}\n' \
                f'Зарегестрировано смертей: {response["deaths"]}\n' \
                f'Смертей за пследние сутки: {response["deaths_delta"]}\n' \
                f'Актуально на {response["date"]}'
    await bot.send_message(message.from_user.id, formed_str)


@dp.message_handler(lambda message: message.text == "Курс валют")
async def currency_message(message: types.Message):
    response = requests.get('https://www.cbr-xml-daily.ru/latest.js').json()["rates"]
    formed_str = f'Текущий курс:\n' \
                 f'1 USD = {round(1/response["USD"], 2)}\n' \
                 f'1 EUR = {round(1/response["EUR"], 2)}'
    await bot.send_message(message.from_user.id, formed_str)


@dp.message_handler(lambda message: message.text == "Случайная новость с панорамы")
async def panorama_message(message: types.Message):
    main_page = requests.get("https://panorama.pub/")
    soup = BeautifulSoup(main_page.text, 'lxml')
    news = soup.select('.news .entry')
    selected_news = random.choice(news)
    news_header = selected_news.select('h3')[0].text.replace("</h3>", '').replace("<h3>", '')
    await bot.send_message(message.from_user.id, news_header)


@dp.message_handler(lambda message: message.text == "Подбросить монетку")
async def panorama_message(message: types.Message):
    coin_state = random.randint(0, 1)
    if coin_state == 0:
        coin_state = 'Орел'
    else:
        coin_state = 'Решка'
    await bot.send_message(message.from_user.id, coin_state)


@dp.message_handler(commands=['track'])
async def track(message: types.Message):
    track_code = await check_track(message.get_args())
    if track_code and track_code != '':
        await bot.send_message(message.from_user.id, track_code)


@dp.message_handler(lambda message: message.text == "Помощь")
async def info_message(message: types.Message):
    await bot.send_message(message.from_user.id, 'Привет! Я бот, который умеет:\n'
                                                 '■Рассказать о курсе валют\n'
                                                 '■Выдать случайную юмористическую новость ИА "Панорама"\n'
                                                 '■Представить статистику заболеваемости COVID-19 в Москве\n'
                                                 '■Подбросить монетку для принятия сложных решений ',
                           reply_markup=mainWindowKb)


async def check_track(track):
    try:
        if track == '': return 'Пустой трек код'
        url = 'https://www.pochta.ru/tracking'
        data = {
            'p_p_id': 'trackingPortlet_WAR_portalportlet',
            'p_p_lifecycle': '2',
            'p_p_resource_id': 'tracking.get-by-barcodes',
            'barcodes': track
        }
        r = requests.post(url, data=data)
        result = json.loads(r.text)
        if 'error' in result:
            print(result['error']['description'])
            return result['error']['description']

        status = result['response'][0]['trackingItem']['globalStatus']
        if status == 'IN_PROGRESS': status = 'В пути'
        if status == 'ARRIVED': status = 'Ожидает в отделении'
        if status == 'ARCHIVED': status = 'Получено адресатом'
        print(status)

        try:
            human_status = result['response'][0]['trackingItem']['trackingHistoryItemList'][0]['humanStatus']
            description = result['response'][0]['trackingItem']['trackingHistoryItemList'][0]['description']
            print(f'{human_status}, {description}')
            return f'{human_status}, {description}'
        except:
            print(f'Возникла ошибка {e}')
            return 'Информация об отправлении временно недоступна'
    except:
        return 'Ошибка во время отслеживания'


if __name__ == '__main__':
    executor.start_polling(dp)

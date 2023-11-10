import telebot
from telebot import types
import time
import hotelrequests
from datetime import datetime
import user

bot = telebot.TeleBot('TOKEN')


def register_command(message, command: str):
    user.User.get_user(message.from_user.id).count_action += 1
    user.User.get_user(message.from_user.id).history.append({user.User.get_user(message.from_user.id).count_action:
                                                                 {'command': command, 'time_of_creating':
                                                                     datetime.now().strftime("%H:%M:%S")}})


@bot.message_handler(commands=['start'])  # Декоратор, который принимает команду 'start' в телеграмме
def send_welcome(message):
    """Задекорированная функция, которая отвечает на команду '/start', проверяет есть ли пользователь, если пользователь
    существует, то выводит сообщение, если пользователя нет, то создает нового пользователя и потом создает клавиатуру
    с кнопками"""
    if user.User.all_users.get(message.from_user.id) is None:
        bot.send_message(message.chat.id, "Добрый день, мы рады Вас видеть!"
                                          "\nЕсли Вам нужна помощь, напишите команду /help")
        user.User(message.from_user.id)
    else:
        bot.send_message(message.chat.id, "Мы рады Вас видеть снова!")

    register_command(message=message, command='start')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    low_price_btn = types.KeyboardButton("Самые дешевые отели")
    high_price_btn = types.KeyboardButton("Самые дорогие отели")
    best_deal_btn = types.KeyboardButton("Отели наиболее подходящих по цене и расположению от центра")
    history_btn = types.KeyboardButton("Моя история")
    markup.add(low_price_btn, high_price_btn, history_btn, best_deal_btn)
    bot.send_message(message.chat.id, 'В меню вы можете выбрать действие, которое хотите совершить',
                     reply_markup=markup)


@bot.message_handler(commands=['help'])  # Декоратор, который принимает команду 'help' в телеграмме
def send_help_text(message):
    """Задекорированная функция, которая отвечает на команду '/help' и выводит сообщение"""
    register_command(message=message, command='help')
    bot.send_message(message.chat.id, "Что может бот: "
                                      "\n/lowprice - вывод самых дешёвых отелей в городе "
                                      "\n/highprice — вывод самых дорогих отелей в городе "
                                      "\n/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от "
                                      "центра "
                                      "\n/history — вывод истории поиска отелей")


@bot.message_handler(commands=['lowprice'])  # Декоратор, который принимает команду 'lowprice' в телеграмме
def lowprice(message):
    """Задекорированная функция, которая отвечает на команду '/lowprice', задает вопрос и регистрирует следующую
    функцию"""
    user.User.get_user(message.from_user.id).sort_order = 'PRICE'
    user.User.get_user(message.from_user.id).if_photo_for_hotels = False
    register_command(message=message, command='lowprice')

    bot.send_message(message.chat.id, 'Давайте подберем вам самые дешевые отели!'
                                      '\nВ какой город направляетесь ?')
    bot.register_next_step_handler(message, set_city)


@bot.message_handler(commands=['highprice'])  # Декоратор, который принимает команду 'highprice' в телеграмме
def highprice(message):
    """Задекорированная функция, которая отвечает на команду '/highprice', задает вопрос и регистрирует следующую
    функцию"""
    user.User.get_user(message.from_user.id).if_photo_for_hotels = False
    user.User.get_user(message.from_user.id).sort_order = 'PRICE_HIGHEST_FIRST'
    register_command(message=message, command='highprice')

    bot.send_message(message.chat.id, 'Давайте подберем вам самые дорогие отели!'
                                      '\nВ какой город направляетесь ?')
    bot.register_next_step_handler(message, set_city)


@bot.message_handler(commands=['bestdeal'])  # Декоратор, который принимает команду 'bestdeal' в телеграмме
def bestdeal(message):
    """Задекорированная функция, которая отвечает на команду '/bestdeal', задает вопрос и регистрирует следующую
    функцию"""
    user.User.get_user(message.from_user.id).if_photo_for_hotels = False
    user.User.get_user(message.from_user.id).sort_order = 'BEST_SELLER'
    register_command(message=message, command='bestdeal')

    bot.send_message(message.chat.id, 'Давайте подберем вам самые подходящие отели!'
                                      '\nКакая минимальная цена для поиска отеля ?')
    bot.register_next_step_handler(message, set_min_price)


@bot.message_handler(commands=['history'])  # Декоратор, который принимает команду 'history' в телеграмме
def history(message):
    """Задекорированная функция, которая отвечает на команду '/history' и выводит всю историю пользователя"""
    register_command(message=message, command='history')
    user_history_dict = user.User.get_user(message.from_user.id).history
    if not user_history_dict:
        bot.send_message(message.from_user.id, 'Здесь пусто!')
    else:
        for i_actions in user_history_dict:
            for i_action in i_actions:
                bot.send_message(message.from_user.id, f'Команда: {i_actions[i_action]["command"]} '
                                                       f'Время: {i_actions[i_action]["time_of_creating"]}')
                try:
                    if i_actions[i_action]['hotels']:
                        bot.send_message(message.from_user.id, 'Отели которые были найдены:')
                        for i_hotels in i_actions[i_action]['hotels']:
                            bot.send_message(message.from_user.id, i_hotels)
                except KeyError:
                    pass


def set_min_price(message):
    """Функция, которая принимает сообщение, проверяет его валидность и записывает минимальную цену для поиска отеля"""
    try:

        if int(message.text) < 0:
            bot.send_message(message.from_user.id, 'Вы ввели число ниже 0, попробуйте заново')
            bot.send_message(message.chat.id, 'Какая минимальная цена для поиска отеля ?')
            bot.register_next_step_handler(message, set_min_price)
        else:
            user.User.get_user(message.from_user.id).min_price = message.text
            bot.send_message(message.chat.id, 'Какая максимальная цена для поиска отеля ?')
            bot.register_next_step_handler(message, set_max_price)

    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка! Введите число, а не строку')
        bot.send_message(message.chat.id, 'Какая минимальная цена для поиска отеля ?')
        bot.register_next_step_handler(message, set_min_price)


def set_max_price(message):
    """Функция, которая принимает сообщение, проверяет его валидность и записывает максимальную цену для поиска отеля"""
    try:

        if int(message.text) < 0:
            bot.send_message(message.from_user.id, 'Вы ввели число ниже 0, попробуйте заново')
            bot.send_message(message.chat.id, 'Какая максимальная цена для поиска отеля ?')
            bot.register_next_step_handler(message, set_max_price)
        elif int(message.text) < int(user.User.get_user(message.from_user.id).min_price):
            bot.send_message(message.from_user.id, 'Вы ввели число ниже минимального числа, попробуйте заново')
            bot.send_message(message.chat.id, 'Какая максимальная цена для поиска отеля ?')
            bot.register_next_step_handler(message, set_max_price)
        else:
            user.User.get_user(message.from_user.id).max_price = message.text
            bot.send_message(message.chat.id, 'Какая минимальная дистанция от центра города ?')
            bot.register_next_step_handler(message, set_min_distance)

    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка! Введите число, а не строку')
        bot.send_message(message.chat.id, 'Какая максимальная цена для поиска отеля ?')
        bot.register_next_step_handler(message, set_max_price)


def set_min_distance(message):
    """Функция, которая принимает сообщение, проверяет его валидность и записывает минимальную дистанцию для поиска
    отеля"""
    try:

        if float(message.text) < 0:
            bot.send_message(message.from_user.id, 'Вы ввели число ниже 0, попробуйте заново')
            bot.send_message(message.chat.id, 'Какая минимальная дистанция от центра города ?')
            bot.register_next_step_handler(message, set_min_distance)
        else:
            user.User.get_user(message.from_user.id).min_d = message.text
            bot.send_message(message.chat.id, 'Какая максимальная дистанция от центра города ?')
            bot.register_next_step_handler(message, set_max_distance)

    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка! Введите число, а не строку')
        bot.send_message(message.chat.id, 'Какая минимальная дистанция от центра города ?')
        bot.register_next_step_handler(message, set_min_distance)


def set_max_distance(message):
    """Функция, которая принимает сообщение, проверяет его валидность и записывает максимальную дистанцию для поиска
    отеля"""
    try:

        if float(message.text) < 0:
            bot.send_message(message.from_user.id, 'Вы ввели число ниже 0, попробуйте заново')
            bot.send_message(message.chat.id, 'Какая максимальная дистанция от центра города ?')
            bot.register_next_step_handler(message, set_max_distance)
        elif float(message.text) < float(user.User.get_user(message.from_user.id).min_d):
            bot.send_message(message.from_user.id, 'Вы ввели число ниже минимального числа, попробуйте заново')
            bot.send_message(message.chat.id, 'Какая максимальная дистанция от центра города ?')
            bot.register_next_step_handler(message, set_max_distance)
        else:
            user.User.get_user(message.from_user.id).max_d = message.text
            bot.send_message(message.chat.id, 'Какой город вы планируете посетить ?')
            bot.register_next_step_handler(message, set_city)

    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка! Введите число, а не строку')
        bot.send_message(message.chat.id, 'Какая максимальная дистанция от центра города ?')
        bot.register_next_step_handler(message, set_max_distance)


def set_city(message):
    """Функция, которая принимает сообщение пользователя, делает запрос по API, находит id города, сохраняет его как
    id города и регистрирует следующую функцию"""

    city_id = hotelrequests.find_location(message.text)

    if city_id is None:
        bot.send_message(message.chat.id, 'Такого города не существует! Проверьте ввод и попробуйте заново')
        bot.send_message(message.chat.id, 'Давайте подберем вам самые дешевые отели! '
                                          '\nВ какой город направляетесь ?')
        bot.register_next_step_handler(message, set_city)
    else:
        user.User.get_user(message.from_user.id).city_id = city_id
        bot.send_message(message.chat.id, 'Сколько отелей показать Вам ? Максимум: 25')
        bot.register_next_step_handler(message, check_and_set_amount_of_hotels)


def check_and_set_amount_of_hotels(message):
    """Функция, которая принимает сообщение пользователя, проверяет его на число и сохраняет его как количество отелей
    для вывода пользователю. После этого создает кнопки для ответа на вопрос"""
    try:

        if int(message.text) > 25:
            bot.send_message(message.chat.id, 'Вы превысили максиму. Максимум для показа отелей: 25'
                                              '\nСколько отелей показать Вам ?')
            bot.register_next_step_handler(message, check_and_set_amount_of_hotels)
        elif int(message.text) <= 0:
            bot.send_message(message.chat.id, 'Вы ввели число ниже 0, попробуйте заново'
                                              '\nСколько фотографий желаете выводить ?')
            bot.register_next_step_handler(message, check_and_set_amount_of_hotels)
        else:
            user.User.get_user(message.from_user.id).amount_of_hotels = message.text

            keyboard = types.InlineKeyboardMarkup()
            key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
            keyboard.add(key_yes)
            key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
            keyboard.add(key_no)
            question = 'Показывать ли Вам фотографии отеля ?'
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка! Введите число, а не строку')
        bot.send_message(message.chat.id, 'Сколько отелей показать Вам ? Максимум: 50')
        bot.register_next_step_handler(message, check_and_set_amount_of_hotels)


@bot.callback_query_handler(func=lambda call: True)
def if_photo_for_hotels(call):
    """Задекорированная функция, которая принимает информацию о нажатии кнопки пользователем, проверяет ответ и после
    это либо запрашивает количество фотографий для вывода либо даты для выезда в отель и регистрирует след функцию"""
    if call.data == "yes":
        user.User.get_user(call.from_user.id).if_photo_for_hotels = True

        bot.send_message(call.message.chat.id, 'Сколько фотографий желаете выводить ? Максимум: 10')
        bot.register_next_step_handler(call.message, set_amount_of_photos)
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'В какие даты планируете прибыть в отель ?'
                                               '\nВведите в формате yyyy-mm-dd')
        bot.register_next_step_handler(call.message, set_check_in_date)


def set_amount_of_photos(message):
    """Функция, которая принимает сообщение пользователя, проверяет его и исходя из проверки либо сохраняет значение
    как количество фотографий для вывода либо запрашивает дату для въезда в отель и регистрирует след функцию"""
    try:

        if int(message.text) > 10:
            bot.send_message(message.chat.id, 'Вы превысили максимум. Максимум для показа фотографий: 10'
                                              '\nСколько фотографий желаете выводить ?')
            bot.register_next_step_handler(message, set_amount_of_photos)
        elif int(message.text) <= 0:
            bot.send_message(message.chat.id, 'Вы ввели число ниже 0, попробуйте заново'
                                              '\nСколько фотографий желаете выводить ?')
            bot.register_next_step_handler(message, set_amount_of_photos)
        else:
            user.User.get_user(message.from_user.id).amount_of_photos = message.text

            bot.send_message(message.chat.id, 'В какие даты планируете прибыть в отель ?'
                                              '\nВведите в формате yyyy-mm-dd')
            bot.register_next_step_handler(message, set_check_in_date)

    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка! Введите число, а не строку')
        bot.send_message(message.chat.id, 'Сколько фотографий желаете выводить ? Максимум: 10')
        bot.register_next_step_handler(message, set_amount_of_photos)


def set_check_in_date(message):
    """Функция, которая принимает сообщение пользователя, проверяет его и исходя из проверки либо сохраняет значение
    как дата въезда либо переспрашивает дату въезда и регистрирует след функцию"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        if bool(datetime.strptime(message.text, '%Y-%m-%d')) and \
                datetime.strptime(message.text, '%Y-%m-%d') >= datetime.strptime(today, '%Y-%m-%d'):
            user.User.get_user(message.from_user.id).check_in_date = message.text

            bot.send_message(message.chat.id, 'В какие даты планируете отъезд с отеля ?'
                                              '\nВведите в формате yyyy-mm-dd')
            bot.register_next_step_handler(message, set_check_out_date)
        else:
            bot.send_message(message.chat.id, 'Ошибка, проверьте дату и введите ее еще раз '
                                              '\nВведите в формате yyyy-mm-dd')
            bot.register_next_step_handler(message, set_check_in_date)
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка, проверьте дату и введите ее еще раз '
                                          '\nВведите в формате yyyy-mm-dd')
        bot.register_next_step_handler(message, set_check_in_date)


def set_check_out_date(message):
    """Функция, которая принимает сообщение пользователя, проверяет его и исходя из проверки либо сохраняет значение
    как дата выезда либо переспрашивает дату выезда и регистрирует след функцию"""
    try:
        if bool(datetime.strptime(message.text, '%Y-%m-%d')) and \
                datetime.strptime(message.text, '%Y-%m-%d') > \
                datetime.strptime(user.User.get_user(message.from_user.id).check_in_date, '%Y-%m-%d'):

            user.User.get_user(message.from_user.id).check_out_date = message.text
            start_search(message.from_user.id)
        else:
            bot.send_message(message.chat.id, 'Ошибка, проверьте дату и введите ее еще раз '
                                              '\nВведите в формате yyyy-mm-dd')
            bot.register_next_step_handler(message, set_check_out_date)

    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка, проверьте дату и введите ее еще раз '
                                          '\nВведите в формате yyyy-mm-dd')
        bot.register_next_step_handler(message, set_check_out_date)


def start_search(user_id):
    """Функция, которая принимает id чата пользователя и начинает поиск отелей. После чего выводит сообщения
    пользователю"""
    bot.send_message(user_id, 'Начинаю поиск отелей...')
    user_dict = user.User.get_user(user_id)
    check_in_date = user_dict.check_in_date
    check_out_date = user_dict.check_out_date
    amount_days_to_stay = datetime.strptime(check_out_date, '%Y-%m-%d') - datetime.strptime(check_in_date, '%Y-%m-%d')
    results = list()

    for i_actions in user_dict.history:
        for i_action in i_actions:
            if i_action == user_dict.count_action:
                i_actions[user_dict.count_action]['hotels'] = list()

    if user_dict.sort_order == 'BEST_SELLER':
        bot.send_message(user_id, 'Собираю данные отелей...')
        response = hotelrequests.find_hotels(city_id=user_dict.city_id,
                                             amount_of_hotels='25',
                                             check_in_date=check_in_date,
                                             check_out_date=check_out_date,
                                             sort_order=user_dict.sort_order,
                                             min_price=user_dict.min_price,
                                             max_price=user_dict.max_price, )

        bot.send_message(user_id, 'Фильтрую результат по Вашему запросу...')
        count_hotels = 0
        min_d = float(user_dict.min_d)
        max_d = float(user_dict.max_d)
        for i_hotels in response['data']['body']['searchResults']['results']:
            distance_from_center = i_hotels["landmarks"][0]["distance"].split()
            distance_from_center = distance_from_center[0]
            distance_from_center = float(distance_from_center.replace(',', '.'))
            if count_hotels < int(user_dict.amount_of_hotels):
                if min_d <= distance_from_center <= max_d:
                    results.append(i_hotels)
                    count_hotels += 1
            else:
                break

    else:
        bot.send_message(user_id, 'Собираю данные отелей...')
        response = hotelrequests.find_hotels(city_id=user_dict.city_id,
                                             amount_of_hotels=user_dict.amount_of_hotels,
                                             check_in_date=check_in_date,
                                             check_out_date=check_out_date,
                                             sort_order=user_dict.sort_order, )

        bot.send_message(user_id, 'Загружаю полученный результат...')
        results = response['data']['body']['searchResults']['results']

    if results:

        if user_dict.if_photo_for_hotels:
            try:
                for i_hotels in results:
                    hotel_id = i_hotels["id"]
                    response_photo = hotelrequests.get_hotel_photos(hotel_id=hotel_id)
                    list_of_photos = list()
                    for i_photos in response_photo['hotelImages']:
                        if len(list_of_photos) != int(user_dict.amount_of_photos):
                            list_of_photos.append(i_photos['baseUrl'].format(size='z'))
                        else:
                            break

                    hotel_price = i_hotels["ratePlan"]["price"]["current"]

                    try:
                        check_address = i_hotels["address"]["streetAddress"]

                        bot.send_media_group(user_id,
                                             [telebot.types.InputMediaPhoto(photo) for photo in list_of_photos])

                        bot.send_message(user_id, f'Название отеля: {i_hotels["name"]}'
                                                  f'\nАдрес: {check_address}'
                                                  f'\nРасстояние от центра: {i_hotels["landmarks"][0]["distance"]}'
                                                  f'\nЦена за ночь: {hotel_price}'
                                                  f'\nЦена за {amount_days_to_stay.days} дня: '
                                                  f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                                  f'\nСсылка на отель: https://www.hotels.com/ho{hotel_id}'
                                         )

                        for i_actions in user_dict.history:
                            for i_check_hist in i_actions:
                                if i_check_hist == user_dict.count_action:
                                    i_actions[user_dict.count_action]['hotels'].append(
                                        f'Название отеля: {i_hotels["name"]}'
                                        f'\nАдрес: {i_hotels["address"]["streetAddress"]}'
                                        f'\nРасстояние от центра: {i_hotels["landmarks"][0]["distance"]}'
                                        f'\nЦена за ночь: {hotel_price}'
                                        f'\nЦена за {amount_days_to_stay.days} дня: '
                                        f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                        f'\nСсылка на отель: https://www.hotels.com/ho{hotel_id}'
                                    )
                                else:
                                    pass

                        time.sleep(2)

                    except KeyError:
                        bot.send_media_group(user_id,
                                             [telebot.types.InputMediaPhoto(photo) for photo in list_of_photos])

                        bot.send_message(user_id, f'Название отеля: {i_hotels["name"]}'
                                                  f'\nАдрес: {i_hotels["address"]["locality"]}'
                                                  f'\nРасстояние от центра: {i_hotels["landmarks"][0]["distance"]}'
                                                  f'\nЦена: {hotel_price}'
                                                  f'\nЦена за {amount_days_to_stay.days} дня: '
                                                  f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                                  f'\nСсылка на отель: https://www.hotels.com/ho{hotel_id}'
                                         )

                        for i_actions in user_dict.history:
                            for i_check_hist in i_actions:
                                if i_check_hist == user_dict.count_action:
                                    i_actions[user_dict.count_action]['hotels'].append(
                                        f'Название отеля: {i_hotels["name"]}'
                                        f'\nАдрес: {i_hotels["address"]["locality"]}'
                                        f'\nРасстояние от центра: {i_hotels["landmarks"][0]["distance"]}'
                                        f'\nЦена: {hotel_price}'
                                        f'\nЦена за {amount_days_to_stay.days} дня: '
                                        f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                        f'\nСсылка на отель: https://www.hotels.com/ho{hotel_id}'
                                    )
                                else:
                                    pass

                        time.sleep(2)

            except KeyError:
                bot.send_message(user_id, 'Ошибка в получение данных от сервера')

            except Exception:
                bot.send_message(user_id, 'Что-то пошло не так!')


        else:
            try:
                for i_hotels in results:
                    hotel_id = i_hotels["id"]
                    hotel_price = i_hotels["ratePlan"]["price"]["current"]
                    try:
                        bot.send_message(user_id, f'Название отеля: {i_hotels["name"]}'
                                                  f'\nАдрес: {i_hotels["address"]["streetAddress"]}'
                                                  f'\nРасстояние от центра: {i_hotels["landmarks"][0]["distance"]}'
                                                  f'\nЦена: {hotel_price}'
                                                  f'\nЦена за {amount_days_to_stay.days} дня: '
                                                  f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                                  f'\nСсылка на отель: https://www.hotels.com/ho{hotel_id}'
                                         )

                        for i_actions in user_dict.history:
                            for i_check_hist in i_actions:
                                if i_check_hist == user_dict.count_action:
                                    i_actions[user_dict.count_action]['hotels'].append(
                                        f'Название отеля: {i_hotels["name"]}'
                                        f'\nАдрес: {i_hotels["address"]["streetAddress"]}'
                                        f'\nРасстояние от центра: {i_hotels["landmarks"][0]["distance"]}'
                                        f'\nЦена: {hotel_price}'
                                        f'\nЦена за {amount_days_to_stay.days} дня: '
                                        f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                        f'\nСсылка на отель: https://www.hotels.com/ho{hotel_id}'
                                    )
                                else:
                                    pass

                        time.sleep(2)

                    except KeyError:
                        bot.send_message(user_id, f'Название отеля: {i_hotels["name"]}'
                                                  f'\nАдрес: {i_hotels["address"]["locality"]}'
                                                  f'\nРасстояние от центра: {i_hotels["landmarks"][0]["distance"]}'
                                                  f'\nЦена: {hotel_price}'
                                                  f'\nЦена за {amount_days_to_stay.days} дня: '
                                                  f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                                  f'\nСсылка на отель: https://www.hotels.com/ho{hotel_id}'
                                         )

                        for i_actions in user_dict.history:
                            for i_check_hist in i_actions:
                                if i_check_hist == user_dict.count_action:
                                    i_actions[user_dict.count_action]['hotels'].append(
                                        f'Название отеля: {i_hotels["name"]}'
                                        f'\nАдрес: {i_hotels["address"]["locality"]}'
                                        f'\nРасстояние от центра: {i_hotels["landmarks"][0]["distance"]}'
                                        f'\nЦена: {hotel_price}'
                                        f'\nЦена за {amount_days_to_stay.days} дня: '
                                        f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                        f'\nСсылка на отель: https://www.hotels.com/ho{hotel_id}'
                                    )
                                else:
                                    pass

                        time.sleep(2)

            except KeyError:
                bot.send_message(user_id, 'Ошибка в получение данных от сервера')

            except Exception:
                bot.send_message(user_id, 'Что-то пошло не так!')

    else:
        bot.send_message(user_id, 'К сожалению, по Вашему запросу ничего нет')


@bot.message_handler(content_types=['text'])  # Декоратор, который принимает текст пользователя
def answer_on_hello(message):
    """Функция, которая принимает сообщение пользователя и сравнивает его. Если ничего не найдено, то выводит сообщение
    об ошибке"""
    if message.text == 'Привет':
        bot.send_message(message.chat.id, "Привет, друг!")
    elif message.text == 'Самые дешевые отели':
        lowprice(message)
    elif message.text == 'Самые дорогие отели':
        highprice(message)
    elif message.text == 'Отели наиболее подходящих по цене и расположению от центра':
        bestdeal(message)
    elif message.text == 'Моя история':
        history(message)
    else:
        bot.send_message(message.chat.id, "Извините, но я не понимаю Вас. Я могу лишь отвечать на 'Привет' или на "
                                          "команды, которые вы можете увидеть в /help")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

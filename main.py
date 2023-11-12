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


@bot.message_handler(commands=['start'])  # A decorator that accepts the 'start' command in a telegram
def send_welcome(message) -> None:
    """
    Decorated function that responds to the '/start' command, checks if the user exists, if the user exists it displays
    a message, if the user doesn't exist it creates a new user and then creates a keyboard keys
    :param message: Message received from a user
    :return None:
    """
    if user.User.all_users.get(message.from_user.id) is None:
        bot.send_message(message.chat.id, "Good afternoon, we are glad to see you!"
                                          "\nIf you need help, write the command /help")
        user.User(message.from_user.id)
    else:
        bot.send_message(message.chat.id, "We are happy to see you again!")

    register_command(message=message, command='start')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    low_price_btn = types.KeyboardButton("Cheapest hotels")
    high_price_btn = types.KeyboardButton("Most expensive hotels")
    best_deal_btn = types.KeyboardButton("Hotels most suitable by price and location from the center")
    history_btn = types.KeyboardButton("My history")
    markup.add(low_price_btn, high_price_btn, history_btn, best_deal_btn)
    bot.send_message(message.chat.id, 'In the menu, you can select the action you want to perform',
                     reply_markup=markup)


@bot.message_handler(commands=['help'])  # A decorator that accepts the 'help' command in a telegram
def send_help_text(message) -> None:
    """
    Decorated function that responds to the '/help' command and outputs a message
    :param message: Message received from a user
    :return None:
    """
    register_command(message=message, command='help')
    bot.send_message(message.chat.id, "What a bot can do: "
                                      "\n/lowprice - the cheapest hotels in the city"
                                      "\n/highprice — the most expensive hotels in the city"
                                      "\n/bestdeal — output of hotels most suitable by price and location "
                                      "from the center"
                                      "\n/history — display hotel search history")


@bot.message_handler(commands=['lowprice'])  # A decorator that accept the command 'lowprice' in a telegram
def lowprice(message) -> None:
    """
    A decorated function that responds to the '/lowprice' command asks a question and registers the next function
    :param message: Message received from a user
    :return None:
    """
    user.User.get_user(message.from_user.id).sort_order = 'PRICE'
    user.User.get_user(message.from_user.id).if_photo_for_hotels = False
    register_command(message=message, command='lowprice')

    bot.send_message(message.chat.id, 'Let us find you the cheapest hotels!'
                                      '\nWhat city are you headed to?')
    bot.register_next_step_handler(message, set_city)


@bot.message_handler(commands=['highprice'])  # A decorator that accepts the command 'highprice' in telegram
def highprice(message) -> None:
    """
    A decorated function that responds to the '/highprice' command asks a question and registers the next function
    :param message: Message received from a user
    :return None:
    """
    user.User.get_user(message.from_user.id).if_photo_for_hotels = False
    user.User.get_user(message.from_user.id).sort_order = 'PRICE_HIGHEST_FIRST'
    register_command(message=message, command='highprice')

    bot.send_message(message.chat.id, 'Let us find you the most expensive hotels!'
                                      '\nWhat city are you headed to?')
    bot.register_next_step_handler(message, set_city)


@bot.message_handler(commands=['bestdeal'])  # A decorator that accepts the 'bestdeal' command in a telegram
def bestdeal(message) -> None:
    """
    A decorated function that responds to the '/bestdeal' command asks a question and registers the next function
    :param message: Message received from a user
    :return None:
    """
    user.User.get_user(message.from_user.id).if_photo_for_hotels = False
    user.User.get_user(message.from_user.id).sort_order = 'BEST_SELLER'
    register_command(message=message, command='bestdeal')

    bot.send_message(message.chat.id, 'Let us find you the most suitable hotels!'
                                      '\nWhat is the minimum price to find a hotel ?')
    bot.register_next_step_handler(message, set_min_price)


@bot.message_handler(commands=['history'])  # A decorator that accepts the 'history' command in a telegram
def history(message) -> None:
    """
    A decorated function that responds to the '/history' command and outputs the user's entire history
    :param message: Message received from a user
    :return None:
    """
    register_command(message=message, command='history')
    user_history_dict = user.User.get_user(message.from_user.id).history
    if not user_history_dict:
        bot.send_message(message.from_user.id, "It's empty!")
    else:
        for i_actions in user_history_dict:
            for i_action in i_actions:
                bot.send_message(message.from_user.id, f'Command: {i_actions[i_action]["command"]} '
                                                       f'Time: {i_actions[i_action]["time_of_creating"]}')
                try:
                    if i_actions[i_action]['hotels']:
                        bot.send_message(message.from_user.id, 'Hotels that have been found:')
                        for i_hotels in i_actions[i_action]['hotels']:
                            bot.send_message(message.from_user.id, i_hotels)
                except KeyError:
                    pass


def set_min_price(message) -> None:
    """
    A function that accepts a message, checks its validity, and records the minimum price to search for a hotel
    :param message: Message received from a user
    :return None:
    """
    try:

        if int(message.text) < 0:
            bot.send_message(message.from_user.id, 'You entered a number lower than 0, try again')
            bot.send_message(message.chat.id, 'What is the minimum price to find a hotel ?')
            bot.register_next_step_handler(message, set_min_price)
        else:
            user.User.get_user(message.from_user.id).min_price = message.text
            bot.send_message(message.chat.id, 'What is the maximum price to find a hotel ?')
            bot.register_next_step_handler(message, set_max_price)

    except ValueError:
        bot.send_message(message.chat.id, 'Error! Enter a number, not a string')
        bot.send_message(message.chat.id, 'What is the minimum price to find a hotel ?')
        bot.register_next_step_handler(message, set_min_price)


def set_max_price(message) -> None:
    """
    A function that accepts a message, checks its validity, and records the maximum price to search for a hotel
    :param message: Message received from a user
    :return None:
    """
    try:

        if int(message.text) < 0:
            bot.send_message(message.from_user.id, 'You entered a number lower than 0, try again')
            bot.send_message(message.chat.id, 'What is the maximum price to find a hotel ?')
            bot.register_next_step_handler(message, set_max_price)
        elif int(message.text) < int(user.User.get_user(message.from_user.id).min_price):
            bot.send_message(message.from_user.id, 'You entered a number below the minimum number, try again')
            bot.send_message(message.chat.id, 'What is the maximum price to find a hotel ?')
            bot.register_next_step_handler(message, set_max_price)
        else:
            user.User.get_user(message.from_user.id).max_price = message.text
            bot.send_message(message.chat.id, 'What is the minimum distance from the city center ?')
            bot.register_next_step_handler(message, set_min_distance)

    except ValueError:
        bot.send_message(message.chat.id, 'Error! Enter a number, not a string')
        bot.send_message(message.chat.id, 'What is the maximum price to find a hotel ?')
        bot.register_next_step_handler(message, set_max_price)


def set_min_distance(message) -> None:
    """
    A function that accepts a message, checks its validity, and records the minimum distance to find a hotel
    :param message: Message received from a user
    :return None:
    """
    try:

        if float(message.text) < 0:
            bot.send_message(message.from_user.id, 'You entered a number lower than 0, try again')
            bot.send_message(message.chat.id, 'What is the minimum distance from the city center ?')
            bot.register_next_step_handler(message, set_min_distance)
        else:
            user.User.get_user(message.from_user.id).min_d = message.text
            bot.send_message(message.chat.id, 'What is the maximum distance from the city center ?')
            bot.register_next_step_handler(message, set_max_distance)

    except ValueError:
        bot.send_message(message.chat.id, 'Error! Enter a number, not a string')
        bot.send_message(message.chat.id, 'What is the minimum distance from the city center ?')
        bot.register_next_step_handler(message, set_min_distance)


def set_max_distance(message) -> None:
    """
    A function that accepts a message, checks its validity, and records the maximum distance to find a hotel
    :param message: Message received from a user
    :return None:
    """
    try:

        if float(message.text) < 0:
            bot.send_message(message.from_user.id, 'You entered a number lower than 0, try again')
            bot.send_message(message.chat.id, 'What is the maximum distance from the city center ?')
            bot.register_next_step_handler(message, set_max_distance)
        elif float(message.text) < float(user.User.get_user(message.from_user.id).min_d):
            bot.send_message(message.from_user.id, 'You entered a number below the minimum number, try again')
            bot.send_message(message.chat.id, 'What is the maximum distance from the city center ?')
            bot.register_next_step_handler(message, set_max_distance)
        else:
            user.User.get_user(message.from_user.id).max_d = message.text
            bot.send_message(message.chat.id, 'Which city are you planning to visit ?')
            bot.register_next_step_handler(message, set_city)

    except ValueError:
        bot.send_message(message.chat.id, 'Error! Enter a number, not a string')
        bot.send_message(message.chat.id, 'What is the maximum distance from the city center ?')
        bot.register_next_step_handler(message, set_max_distance)


def set_city(message) -> None:
    """
    A function that accepts a user message, makes an API request, finds the city id, stores it as a city id and
    registers the next function
    :param message: Message received from a user
    :return None:
    """

    city_id = hotelrequests.find_location(message.text)

    if city_id is None:
        bot.send_message(message.chat.id, 'This city does not exist! Check the input and try again')
        bot.send_message(message.chat.id, 'Let us find you the cheapest hotels!'
                                          '\nWhat city are you headed to?')
        bot.register_next_step_handler(message, set_city)
    else:
        user.User.get_user(message.from_user.id).city_id = city_id
        bot.send_message(message.chat.id, 'How many hotels to show you ? Maximum: 25')
        bot.register_next_step_handler(message, check_and_set_amount_of_hotels)


def check_and_set_amount_of_hotels(message) -> None:
    """
    A function that takes a user's message, checks it for a number, and stores it as the number of hotels
    to output to the user. It then creates buttons to answer the question
    :param message: Message received from a user
    :return None:
    """
    try:

        if int(message.text) > 25:
            bot.send_message(message.chat.id, 'You have exceeded the maximum. Maximum for showing hotels: 25'
                                              '\nHow many hotels to show you ?')
            bot.register_next_step_handler(message, check_and_set_amount_of_hotels)
        elif int(message.text) <= 0:
            bot.send_message(message.chat.id, 'You entered a number lower than 0, try again'
                                              '\nHow many photos do you want to output ?')
            bot.register_next_step_handler(message, check_and_set_amount_of_hotels)
        else:
            user.User.get_user(message.from_user.id).amount_of_hotels = message.text

            keyboard = types.InlineKeyboardMarkup()
            key_yes = types.InlineKeyboardButton(text='Yes', callback_data='yes')
            keyboard.add(key_yes)
            key_no = types.InlineKeyboardButton(text='No', callback_data='no')
            keyboard.add(key_no)
            question = 'Shall I show you pictures of the hotel ?'
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

    except ValueError:
        bot.send_message(message.chat.id, 'Error! Enter a number, not a string')
        bot.send_message(message.chat.id, 'How many hotels to show you ? Maximum: 25')
        bot.register_next_step_handler(message, check_and_set_amount_of_hotels)


@bot.callback_query_handler(func=lambda call: True)
def if_photo_for_hotels(call) -> None:
    """
    A decorated function that accepts information about a button press by the user, checks the response and
    after it either requests the number of photos to output or the dates for checkout and registers a next function
    :param call: Clicked answer on button
    :return None:
    """
    if call.data == "yes":
        user.User.get_user(call.from_user.id).if_photo_for_hotels = True

        bot.send_message(call.message.chat.id, 'How many photos do you want to output ? Maximum: 10')
        bot.register_next_step_handler(call.message, set_amount_of_photos)
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'What dates do you plan to arrive at the hotel ?'
                                               '\nEnter in the format yyyy-mm-dd')
        bot.register_next_step_handler(call.message, set_check_in_date)


def set_amount_of_photos(message) -> None:
    """
    A function that receives a user's message, checks it and based on the check either stores the value as
    the number of photos to output or requests a date for check-in and registers a next function
    :param message: Message received from a user
    :return None:
    """
    try:

        if int(message.text) > 10:
            bot.send_message(message.chat.id, 'You have exceeded the maximum. Maximum for displaying photos: 10'
                                              '\nHow many photos do you want to output ?')
            bot.register_next_step_handler(message, set_amount_of_photos)
        elif int(message.text) <= 0:
            bot.send_message(message.chat.id, 'You entered a number lower than 0, try again'
                                              '\nHow many photos do you want to output ?')
            bot.register_next_step_handler(message, set_amount_of_photos)
        else:
            user.User.get_user(message.from_user.id).amount_of_photos = message.text

            bot.send_message(message.chat.id, 'What dates do you plan to arrive at the hotel ?'
                                              '\nEnter in the format yyyy-mm-dd')
            bot.register_next_step_handler(message, set_check_in_date)

    except ValueError:
        bot.send_message(message.chat.id, 'Error! Enter a number, not a string')
        bot.send_message(message.chat.id, 'How many photos do you want to output ? Maximum: 10')
        bot.register_next_step_handler(message, set_amount_of_photos)


def set_check_in_date(message) -> None:
    """
    A function that receives a user's message, checks it and based on the check either stores the value as
    the entry date or asks the entry date again and registers a next function
    :param message: Message received from a user
    :return None:
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        if bool(datetime.strptime(message.text, '%Y-%m-%d')) and \
                datetime.strptime(message.text, '%Y-%m-%d') >= datetime.strptime(today, '%Y-%m-%d'):
            user.User.get_user(message.from_user.id).check_in_date = message.text

            bot.send_message(message.chat.id, 'On what dates do you plan to leave the hotel ?'
                                              '\nEnter in the format yyyy-mm-dd')
            bot.register_next_step_handler(message, set_check_out_date)
        else:
            bot.send_message(message.chat.id, 'Error, check the date and enter it again'
                                              '\nEnter in the format yyyy-mm-dd')
            bot.register_next_step_handler(message, set_check_in_date)
    except ValueError:
        bot.send_message(message.chat.id, 'Error, check the date and enter it again'
                                          '\nEnter in the format yyyy-mm-dd')
        bot.register_next_step_handler(message, set_check_in_date)


def set_check_out_date(message) -> None:
    """
    A function that receives a user's message, checks it and based on the check either stores the value as
    the departure date or asks the departure date again and registers a next function
    :param message: Message received from a user
    :return None:
    """
    try:
        if bool(datetime.strptime(message.text, '%Y-%m-%d')) and \
                datetime.strptime(message.text, '%Y-%m-%d') > \
                datetime.strptime(user.User.get_user(message.from_user.id).check_in_date, '%Y-%m-%d'):

            user.User.get_user(message.from_user.id).check_out_date = message.text
            start_search(message.from_user.id)
        else:
            bot.send_message(message.chat.id, 'Error, check the date and enter it again'
                                              '\nEnter in the format yyyy-mm-dd')
            bot.register_next_step_handler(message, set_check_out_date)

    except ValueError:
        bot.send_message(message.chat.id, 'Error, check the date and enter it again'
                                          '\nEnter in the format yyyy-mm-dd')
        bot.register_next_step_handler(message, set_check_out_date)


def start_search(user_id) -> None:
    """
    A function that takes a user's chat id and starts searching for hotels. It then displays messages to the user
    :param user_id: User id
    :return None:
    """
    bot.send_message(user_id, "I'm starting a hotel search...")
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
        bot.send_message(user_id, 'Collecting hotel data...')
        response = hotelrequests.find_hotels(city_id=user_dict.city_id,
                                             amount_of_hotels='25',
                                             check_in_date=check_in_date,
                                             check_out_date=check_out_date,
                                             sort_order=user_dict.sort_order,
                                             min_price=user_dict.min_price,
                                             max_price=user_dict.max_price, )

        bot.send_message(user_id, 'Filtering the result according to your request...')
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
        bot.send_message(user_id, 'Collecting hotel data...')
        response = hotelrequests.find_hotels(city_id=user_dict.city_id,
                                             amount_of_hotels=user_dict.amount_of_hotels,
                                             check_in_date=check_in_date,
                                             check_out_date=check_out_date,
                                             sort_order=user_dict.sort_order, )

        bot.send_message(user_id, 'Downloading the result...')
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

                        bot.send_message(user_id, f'Hotel name: {i_hotels["name"]}'
                                                  f'\nAddress: {check_address}'
                                                  f'\nDistance from the center: {i_hotels["landmarks"][0]["distance"]}'
                                                  f'\nPrice per night: {hotel_price}'
                                                  f'\nPrice per {amount_days_to_stay.days} day: '
                                                  f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                                  f'\nHotel link: https://www.hotels.com/ho{hotel_id}'
                                         )

                        for i_actions in user_dict.history:
                            for i_check_hist in i_actions:
                                if i_check_hist == user_dict.count_action:
                                    i_actions[user_dict.count_action]['hotels'].append(
                                        f'Hotel name: {i_hotels["name"]}'
                                        f'\nAddress: {i_hotels["address"]["streetAddress"]}'
                                        f'\nDistance from the center: {i_hotels["landmarks"][0]["distance"]}'
                                        f'\nPrice per night: {hotel_price}'
                                        f'\nPrice per {amount_days_to_stay.days} day: '
                                        f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                        f'\nHotel link: https://www.hotels.com/ho{hotel_id}'
                                    )
                                else:
                                    pass

                        time.sleep(2)

                    except KeyError:
                        bot.send_media_group(user_id,
                                             [telebot.types.InputMediaPhoto(photo) for photo in list_of_photos])

                        bot.send_message(user_id, f'Hotel name: {i_hotels["name"]}'
                                                  f'\nAddress: {i_hotels["address"]["locality"]}'
                                                  f'\nDistance from the center: {i_hotels["landmarks"][0]["distance"]}'
                                                  f'\nPrice: {hotel_price}'
                                                  f'\nPrice per {amount_days_to_stay.days} day: '
                                                  f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                                  f'\nHotel link: https://www.hotels.com/ho{hotel_id}'
                                         )

                        for i_actions in user_dict.history:
                            for i_check_hist in i_actions:
                                if i_check_hist == user_dict.count_action:
                                    i_actions[user_dict.count_action]['hotels'].append(
                                        f'Hotel name: {i_hotels["name"]}'
                                        f'\nAddress: {i_hotels["address"]["locality"]}'
                                        f'\nDistance from the center: {i_hotels["landmarks"][0]["distance"]}'
                                        f'\nPrice: {hotel_price}'
                                        f'\nPrice per {amount_days_to_stay.days} day: '
                                        f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                        f'\nHotel link: https://www.hotels.com/ho{hotel_id}'
                                    )
                                else:
                                    pass

                        time.sleep(2)

            except KeyError:
                bot.send_message(user_id, 'Error in receiving data from the server')

            except Exception:
                bot.send_message(user_id, "Something's gone wrong!")


        else:
            try:
                for i_hotels in results:
                    hotel_id = i_hotels["id"]
                    hotel_price = i_hotels["ratePlan"]["price"]["current"]
                    try:
                        bot.send_message(user_id, f'Hotel name: {i_hotels["name"]}'
                                                  f'\nAddress: {i_hotels["address"]["streetAddress"]}'
                                                  f'\nDistance from the center: {i_hotels["landmarks"][0]["distance"]}'
                                                  f'\nPrice: {hotel_price}'
                                                  f'\nPrice per {amount_days_to_stay.days} day: '
                                                  f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                                  f'\nHotel link: https://www.hotels.com/ho{hotel_id}'
                                         )

                        for i_actions in user_dict.history:
                            for i_check_hist in i_actions:
                                if i_check_hist == user_dict.count_action:
                                    i_actions[user_dict.count_action]['hotels'].append(
                                        f'Hotel name: {i_hotels["name"]}'
                                        f'\nAddress: {i_hotels["address"]["streetAddress"]}'
                                        f'\nDistance from the center: {i_hotels["landmarks"][0]["distance"]}'
                                        f'\nPrice: {hotel_price}'
                                        f'\nPrice per {amount_days_to_stay.days} day: '
                                        f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                        f'\nHotel link: https://www.hotels.com/ho{hotel_id}'
                                    )
                                else:
                                    pass

                        time.sleep(2)

                    except KeyError:
                        bot.send_message(user_id, f'Hotel name: {i_hotels["name"]}'
                                                  f'\nAddress: {i_hotels["address"]["locality"]}'
                                                  f'\nDistance from the center: {i_hotels["landmarks"][0]["distance"]}'
                                                  f'\nPrice: {hotel_price}'
                                                  f'\nPrice per {amount_days_to_stay.days} day: '
                                                  f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                                  f'\nHotel link: https://www.hotels.com/ho{hotel_id}'
                                         )

                        for i_actions in user_dict.history:
                            for i_check_hist in i_actions:
                                if i_check_hist == user_dict.count_action:
                                    i_actions[user_dict.count_action]['hotels'].append(
                                        f'Hotel name: {i_hotels["name"]}'
                                        f'\nAddress: {i_hotels["address"]["locality"]}'
                                        f'\nDistance from the center: {i_hotels["landmarks"][0]["distance"]}'
                                        f'\nPrice: {hotel_price}'
                                        f'\nPrice per {amount_days_to_stay.days} day: '
                                        f'${amount_days_to_stay.days * int(hotel_price.replace("$", "").replace(",", ""))}'
                                        f'\nHotel link: https://www.hotels.com/ho{hotel_id}'
                                    )
                                else:
                                    pass

                        time.sleep(2)

            except KeyError:
                bot.send_message(user_id, 'Error in receiving data from the server')

            except Exception:
                bot.send_message(user_id, "Something's gone wrong!")

    else:
        bot.send_message(user_id, 'Unfortunately, there is nothing for your request')


@bot.message_handler(content_types=['text'])  # A decorator that accepts the user's text
def answer_on_hello(message) -> None:
    """
    A function that takes a user's message and compares it. If nothing is found, it outputs an error message
    :param message: Message received from a user
    :return None:
    """
    if message.text == 'Hi':
        bot.send_message(message.chat.id, "Hey, buddy!")
    elif message.text == 'Cheapest hotels':
        lowprice(message)
    elif message.text == 'Most expensive hotels':
        highprice(message)
    elif message.text == 'Hotels most suitable by price and location from the center':
        bestdeal(message)
    elif message.text == 'My history':
        history(message)
    else:
        bot.send_message(message.chat.id, "I'm sorry, but I don't understand you. I can only reply to 'Hi' "
                                          "or to the commands you can see in /help")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

import requests
import json
from typing import Optional

headers = {
    'X-RapidAPI-Key': 'API KEY',
    'X-RapidAPI-Host': 'hotels4.p.rapidapi.com'
}


def find_location(city: str):
    url = "https://hotels4.p.rapidapi.com/locations/search"

    querystring = {"query": city, "locale": "en_EN"}

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200:
            result = json.loads(response.text)
            for i_suggested in result['suggestions']:
                for i_entities in i_suggested['entities']:
                    if i_entities['name'] == city:
                        return i_entities['destinationId']
        else:
            return None
    except requests.RequestException:
        return None


def find_hotels(city_id: str, amount_of_hotels: str, check_in_date: str, check_out_date: str, sort_order: str,
                min_price: str = "", max_price: str = "") -> Optional[dict]:
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": amount_of_hotels, "checkIn": check_in_date,
                   "checkOut": check_out_date, "adults1": "1", "priceMin": min_price, "priceMax": max_price,
                   "sortOrder": sort_order, "locale": "ru_RU", "currency": "USD"}

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200:
            result = json.loads(response.text)
        else:
            result = None

    except requests.Timeout:
        result = None
    except requests.RequestException:
        result = None

    return result


def get_hotel_photos(hotel_id):
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": hotel_id}
    response_photo = json.loads(requests.request("GET", url, headers=headers, params=querystring).text)
    return response_photo

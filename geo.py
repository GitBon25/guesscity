import requests


def get_geo_info(city_name, type_info):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
            'geocode': city_name,
            'format': 'json'
        }
        response = requests.get(url, params)
        json_data = response.json()

        if not json_data['response']['GeoObjectCollection']['featureMember']:
            raise ValueError("Город не найден")

        geo_object = json_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

        if type_info == 'coordinates':
            coordinates_str = geo_object['Point']['pos']
            long, lat = map(float, coordinates_str.split())
            return long, lat
        elif type_info == 'country':
            country = geo_object['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['CountryName']
            return country
        else:
            raise ValueError("Неверный тип информации. Используйте 'country' или 'coordinates'")
    except Exception as e:
        return e
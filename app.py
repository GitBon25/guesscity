from flask import Flask, request, jsonify
import os
import random
import requests


app = Flask(__name__)

CITIES = [
    {"name": "москва", "image_id": "965417/61c4036c5ae5394fbbb5"},
    {"name": "москва", "image_id": "1030494/5765e7cfceb84c387b6c"},
    {"name": "нью-йорк", "image_id": "1652229/2e84a53e858977e35a27"},
    {"name": "нью-йорк", "image_id": "1652229/361bf18a372f813d17e3"},
    {"name": "париж", "image_id": "1521359/3bb5bc215c38e44d07e1"},
    {"name": "париж", "image_id": "1540737/cbf6fe4d55036f4a09f6"}
]

HELP_TEXT = (
    "Это игра 'Угадай город'! Я показываю фото города, а ты пытаешься угадать, что это за город. "
    "После правильного ответа тебе нужно будет угадать страну этого города. "
    "Скажи 'да', чтобы начать игру, или 'нет', чтобы отказаться. "
    "После ответа я скажу, правильно ли ты угадал, и предложу сыграть заново. "
    "В любой момент можешь нажать 'Помощь', чтобы увидеть это сообщение. "
    "Готов продолжить?"
)


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
            raise ValueError(
                "Неверный тип информации. Используйте 'country' или 'coordinates'")
    except Exception as e:
        return str(e)


@app.route('/alice', methods=['POST'])
def alice_skill():
    req = request.get_json()
    user_message = req.get("request", {}).get("original_utterance", "").lower()
    session_state = req.get("state", {}).get("session", {})

    current_stage = session_state.get("stage", "initial")
    current_city = session_state.get("current_city", None)
    current_country = session_state.get("current_country", None)

    response = {
        "response": {
            "text": "",
            "tts": "",
            "buttons": [
                {"title": "Да", "hide": True},
                {"title": "Нет", "hide": True},
                {"title": "Помощь", "hide": True}
            ],
            "end_session": False
        },
        "session": {
            "session_id": req["session"]["session_id"],
            "message_id": req["session"]["message_id"],
            "user_id": req["session"]["user_id"]
        },
        "version": "1.0",
        "session_state": {}
    }

    if "помощь" in user_message:
        response["response"]["text"] = HELP_TEXT
        response["response"]["tts"] = HELP_TEXT
        response["session_state"] = {
            "stage": current_stage,
            "current_city": current_city,
            "current_country": current_country
        }
        return jsonify(response)

    if current_stage == "initial":
        if not user_message or "давай сыграем" in user_message:
            response["response"]["text"] = "Привет! Давай сыграем в игру 'Угадай город'? Я покажу фото, а ты назови город. После этого угадаешь страну. Согласен?"
            response["response"]["tts"] = "Привет! Давай сыграем в игру 'Угадай город'? Я покажу фото, а ты назови город. После этого угадаешь страну. Согласен?"
            response["session_state"] = {"stage": "initial"}
        elif "да" in user_message:
            selected_city = random.choice(CITIES)
            response["response"]["text"] = "Отлично! Вот фото города. Какой это город?"
            response["response"]["tts"] = "Отлично! Вот фото города. Какой это город?"
            response["response"]["card"] = {
                "type": "BigImage",
                "image_id": selected_city["image_id"],
                "description": "Что это за город?"
            }
            response["session_state"] = {
                "stage": "awaiting_city_answer",
                "current_city": selected_city["name"]
            }
        else:
            response["response"]["text"] = "Жаль! Если передумаешь, скажи 'давай сыграем'."
            response["response"]["tts"] = "Жаль! Если передумаешь, скажи 'давай сыграем'."
            response["session_state"] = {"stage": "initial"}

    elif current_stage == "awaiting_city_answer":
        if user_message in [city["name"] for city in CITIES]:
            try:
                country = get_geo_info(current_city, 'country')
                if user_message == current_city:
                    response["response"]["text"] = f"Верно! Это {current_city.title()}! Теперь скажи, в какой стране находится этот город?"
                    response["response"]["tts"] = f"Верно! Это {current_city.title()}! Теперь скажи, в какой стране находится этот город?"
                else:
                    response["response"]["text"] = f"Увы, это не {user_message.title()}. Правильный ответ: {current_city.title()}. Теперь скажи, в какой стране находится этот город?"
                    response["response"]["tts"] = f"Увы, это не {user_message.title()}. Правильный ответ: {current_city.title()}. Теперь скажи, в какой стране находится этот город?"

                response["session_state"] = {
                    "stage": "awaiting_country_answer",
                    "current_city": current_city,
                    "current_country": country
                }
            except Exception as e:
                response["response"]["text"] = f"Верно! Это {current_city.title()}! К сожалению, не могу определить страну для этого города. Сыграем ещё раз?"
                response["response"]["tts"] = f"Верно! Это {current_city.title()}! К сожалению, не могу определить страну для этого города. Сыграем ещё раз?"
                response["session_state"] = {"stage": "game_ended"}
        else:
            response["response"]["text"] = "Кажется, такого города нет в игре. Попробуй ещё раз! Какой это город?"
            response["response"]["tts"] = "Кажется, такого города нет в игре. Попробуй ещё раз! Какой это город?"
            response["response"]["card"] = {
                "type": "BigImage",
                "image_id": [city["image_id"] for city in CITIES if city["name"] == current_city][0],
                "description": "Что это за город?"
            }
            response["session_state"] = {
                "stage": "awaiting_city_answer",
                "current_city": current_city
            }

    elif current_stage == "awaiting_country_answer":
        correct_country = current_country.lower()
        user_country = user_message.lower()

        map_url = f"https://yandex.ru/maps/?mode=search&text={current_city}"

        if user_country in correct_country or correct_country in user_country:
            response["response"]["text"] = f"Правильно! {current_city.title()} находится в {current_country}. Молодец! Сыграем ещё раз?"
            response["response"]["tts"] = f"Правильно! {current_city.title()} находится в {current_country}. Молодец! Сыграем ещё раз?"
        else:
            response["response"]["text"] = f"Не совсем. {current_city.title()} находится в {current_country}. Сыграем ещё раз?"
            response["response"]["tts"] = f"Не совсем. {current_city.title()} находится в {current_country}. Сыграем ещё раз?"

        response["response"]["buttons"].append({
            "title": "Показать город на карте",
            "url": map_url,
            "hide": True
        })
        response["session_state"] = {"stage": "game_ended"}

    elif current_stage == "game_ended":
        if "да" in user_message:
            selected_city = random.choice(CITIES)
            response["response"]["text"] = "Отлично! Вот новое фото. Какой это город?"
            response["response"]["tts"] = "Отлично! Вот новое фото. Какой это город?"
            response["response"]["card"] = {
                "type": "BigImage",
                "image_id": selected_city["image_id"],
                "description": "Что это за город?"
            }
            response["session_state"] = {
                "stage": "awaiting_city_answer",
                "current_city": selected_city["name"]
            }
        else:
            response["response"]["text"] = "Спасибо за игру! Если захочешь сыграть снова, скажи 'давай сыграем'."
            response["response"]["tts"] = "Спасибо за игру! Если захочешь сыграть снова, скажи 'давай сыграем'."
            response["session_state"] = {"stage": "initial"}

    return jsonify(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

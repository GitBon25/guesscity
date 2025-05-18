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
    "Также ты можешь сказать 'сменить имя', если хочешь, чтобы я называл тебя по-другому."
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


def get_personalized_message(base_message, user_name):
    if user_name:
        return f"{user_name}, {base_message.lower()}"
    return base_message


@app.route('/alice', methods=['POST'])
def alice_skill():
    req = request.get_json()
    user_message = req.get("request", {}).get("original_utterance", "").lower()
    session_state = req.get("state", {}).get("session", {})

    current_stage = session_state.get("stage", "greeting")
    current_city = session_state.get("current_city", None)
    current_country = session_state.get("current_country", None)
    user_name = session_state.get("user_name", None)

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

    if user_name:
        response["response"]["buttons"].append(
            {"title": "Сменить имя", "hide": True})

    if "помощь" in user_message:
        response["response"]["text"] = HELP_TEXT
        response["response"]["tts"] = HELP_TEXT
        response["session_state"] = {
            "stage": current_stage,
            "current_city": current_city,
            "current_country": current_country,
            "user_name": user_name
        }
        return jsonify(response)

    if "сменить имя" in user_message:
        response["response"]["text"] = "Как тебя зовут?"
        response["response"]["tts"] = "Как тебя зовут?"
        response["session_state"] = {
            "stage": "get_name",
            "current_city": current_city,
            "current_country": current_country
        }
        return jsonify(response)

    if current_stage == "greeting":
        response["response"]["text"] = "Привет! Как тебя зовут?"
        response["response"]["tts"] = "Привет! Как тебя зовут?"
        response["session_state"] = {"stage": "get_name"}

    elif current_stage == "get_name":
        if user_message:
            user_name = user_message.strip().title()
            response["response"]["text"] = f"Приятно познакомиться, {user_name}! Давай сыграем в игру 'Угадай город'? Я покажу фото, а ты назови город. После этого угадаешь страну. Согласен?"
            response["response"]["tts"] = f"Приятно познакомиться, {user_name}! Давай сыграем в игру 'Угадай город'? Я покажу фото, а ты назови город. После этого угадаешь страну. Согласен?"
            response["session_state"] = {
                "stage": "initial",
                "user_name": user_name
            }
        else:
            response["response"]["text"] = "Извини, я не расслышала твоё имя. Пожалуйста, скажи, как тебя зовут?"
            response["response"]["tts"] = "Извини, я не расслышала твоё имя. Пожалуйста, скажи, как тебя зовут?"
            response["session_state"] = {"stage": "get_name"}

    elif current_stage == "initial":
        if not user_message or "давай сыграем" in user_message:
            message = get_personalized_message(
                "Давай сыграем в игру 'Угадай город'? Я покажу фото, а ты назови город. После этого угадаешь страну. Согласен?", user_name)
            response["response"]["text"] = message
            response["response"]["tts"] = message
            response["session_state"] = {
                "stage": "initial",
                "user_name": user_name
            }
        elif "да" in user_message:
            selected_city = random.choice(CITIES)
            message = get_personalized_message(
                "Отлично! Вот фото города. Какой это город?", user_name)
            response["response"]["text"] = message
            response["response"]["tts"] = message
            response["response"]["card"] = {
                "type": "BigImage",
                "image_id": selected_city["image_id"],
                "description": "Что это за город?"
            }
            response["session_state"] = {
                "stage": "awaiting_city_answer",
                "current_city": selected_city["name"],
                "user_name": user_name
            }
        else:
            message = get_personalized_message(
                "Жаль! Если передумаешь, скажи 'давай сыграем'.", user_name)
            response["response"]["text"] = message
            response["response"]["tts"] = message
            response["session_state"] = {
                "stage": "initial",
                "user_name": user_name
            }

    elif current_stage == "awaiting_city_answer":
        if user_message in [city["name"] for city in CITIES]:
            try:
                country = get_geo_info(current_city, 'country')
                if user_message == current_city:
                    message = get_personalized_message(
                        f"Верно! Это {current_city.title()}! Теперь скажи, в какой стране находится этот город?", user_name)
                    response["response"]["text"] = message
                    response["response"]["tts"] = message
                else:
                    message = get_personalized_message(
                        f"Увы, это не {user_message.title()}. Правильный ответ: {current_city.title()}. Теперь скажи, в какой стране находится этот город?", user_name)
                    response["response"]["text"] = message
                    response["response"]["tts"] = message

                response["session_state"] = {
                    "stage": "awaiting_country_answer",
                    "current_city": current_city,
                    "current_country": country,
                    "user_name": user_name
                }
            except Exception as e:
                message = get_personalized_message(
                    f"Верно! Это {current_city.title()}! К сожалению, не могу определить страну для этого города. Сыграем ещё раз?", user_name)
                response["response"]["text"] = message
                response["response"]["tts"] = message
                response["session_state"] = {
                    "stage": "game_ended",
                    "user_name": user_name
                }
        else:
            message = get_personalized_message(
                "Кажется, такого города нет в игре. Попробуй ещё раз! Какой это город?", user_name)
            response["response"]["text"] = message
            response["response"]["tts"] = message
            response["response"]["card"] = {
                "type": "BigImage",
                "image_id": [city["image_id"] for city in CITIES if city["name"] == current_city][0],
                "description": "Что это за город?"
            }
            response["session_state"] = {
                "stage": "awaiting_city_answer",
                "current_city": current_city,
                "user_name": user_name
            }

    elif current_stage == "awaiting_country_answer":
        correct_country = current_country.lower()
        user_country = user_message.lower()

        map_url = f"https://yandex.ru/maps/?mode=search&text={current_city}"

        if user_country in correct_country or correct_country in user_country:
            message = get_personalized_message(
                f"Правильно! {current_city.title()} находится в {current_country}. Молодец! Сыграем ещё раз?", user_name)
            response["response"]["text"] = message
            response["response"]["tts"] = message
        else:
            message = get_personalized_message(
                f"Не совсем. {current_city.title()} находится в {current_country}. Сыграем ещё раз?", user_name)
            response["response"]["text"] = message
            response["response"]["tts"] = message

        response["response"]["buttons"].append({
            "title": "Показать город на карте",
            "url": map_url,
            "hide": True
        })
        response["session_state"] = {
            "stage": "game_ended",
            "user_name": user_name
        }

    elif current_stage == "game_ended":
        if "да" in user_message:
            selected_city = random.choice(CITIES)
            message = get_personalized_message(
                "Отлично! Вот новое фото. Какой это город?", user_name)
            response["response"]["text"] = message
            response["response"]["tts"] = message
            response["response"]["card"] = {
                "type": "BigImage",
                "image_id": selected_city["image_id"],
                "description": "Что это за город?"
            }
            response["session_state"] = {
                "stage": "awaiting_city_answer",
                "current_city": selected_city["name"],
                "user_name": user_name
            }
        else:
            message = get_personalized_message(
                "Спасибо за игру! Если захочешь сыграть снова, скажи 'давай сыграем'.", user_name)
            response["response"]["text"] = message
            response["response"]["tts"] = message
            response["session_state"] = {
                "stage": "initial",
                "user_name": user_name
            }

    return jsonify(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

from flask import Flask, request, jsonify
import os
import random


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
    "Скажи 'да', чтобы начать игру, или 'нет', чтобы отказаться. "
    "После ответа я скажу, правильно ли ты угадал, и предложу сыграть заново. "
    "В любой момент можешь нажать 'Помощь', чтобы увидеть это сообщение. "
    "Готов продолжить?"
)


@app.route('/alice', methods=['POST'])
def alice_skill():
    req = request.get_json()
    user_message = req.get("request", {}).get("original_utterance", "").lower()
    session_state = req.get("state", {}).get("session", {})

    current_stage = session_state.get("stage", "initial")
    current_city = session_state.get("current_city", None)

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
            "stage": current_stage, "current_city": current_city}
        return jsonify(response)

    if current_stage == "initial":
        if not user_message or "давай сыграем" in user_message:
            response["response"]["text"] = "Привет! Давай сыграем в игру 'Угадай город'? Я покажу фото, а ты назови город. Согласен?"
            response["response"]["tts"] = "Привет! Давай сыграем в игру 'Угадай город'? Я покажу фото, а ты назови город. Согласен?"
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
                "stage": "awaiting_answer", "current_city": selected_city["name"]}
        else:
            response["response"]["text"] = "Жаль! Если передумаешь, скажи 'давай сыграем'."
            response["response"]["tts"] = "Жаль! Если передумаешь, скажи 'давай сыграем'."
            response["session_state"] = {"stage": "initial"}

    elif current_stage == "awaiting_answer":
        if user_message in [city["name"] for city in CITIES]:
            map_url = f"https://yandex.ru/maps/?mode=search&text={current_city}"
            if user_message == current_city:
                response["response"]["text"] = f"Верно! Это {current_city.title()}! Молодец! Сыграем ещё раз?"
                response["response"]["tts"] = f"Верно! Это {current_city.title()}! Молодец! Сыграем ещё раз?"
            else:
                response["response"]["text"] = f"Увы, это не {user_message.title()}. Правильный ответ: {current_city.title()}. Сыграем ещё раз?"
                response["response"]["tts"] = f"Увы, это не {user_message.title()}. Правильный ответ: {current_city.title()}. Сыграем ещё раз?"
            response["response"]["buttons"].append({
                "title": "Показать город на карте",
                "url": map_url,
                "hide": True
            })
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
                "stage": "awaiting_answer", "current_city": current_city}

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
                "stage": "awaiting_answer", "current_city": selected_city["name"]}
        else:
            response["response"]["text"] = "Спасибо за игру! Если захочешь сыграть снова, скажи 'давай сыграем'."
            response["response"]["tts"] = "Спасибо за игру! Если захочешь сыграть снова, скажи 'давай сыграем'."
            response["session_state"] = {"stage": "initial"}

    return jsonify(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

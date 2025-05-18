from flask import Flask, request, jsonify
import os


app = Flask(__name__)

HELP_TEXT = (
    "Это игра 'Угадай город'! Я показываю фото города, а ты пытаешься угадать, что это за город. "
    "Скажи 'да', чтобы начать игру, или 'нет', чтобы отказаться. "
    "В любой момент можешь нажать 'Помощь', чтобы увидеть это сообщение. "
    "Готов продолжить?"
)


@app.route('/alice', methods=['POST'])
def alice_skill():
    req = request.get_json()
    user_message = req.get("request", {}).get("original_utterance", "").lower()
    session_state = req.get("state", {}).get(
        "session", {})

    current_stage = session_state.get("stage", "initial")

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
        response["session_state"] = {"stage": current_stage}
        return jsonify(response)

    if current_stage == "initial" and not user_message:
        response["response"]["text"] = "Привет! Давай сыграем в игру? Попробуй отгадать город по фото. Согласен?"
        response["response"]["tts"] = "Привет! Давай сыграем в игру? Попробуй отгадать город по фото. Согласен?"
        response["session_state"] = {"stage": "initial"}
    elif "да" in user_message:
        response["response"]["text"] = "Отлично! Вот фото города. Отгадай, что это за город?"
        response["response"]["tts"] = "Отлично! Вот фото города. Отгадай, что это за город?"
        response["response"]["card"] = {
            "type": "BigImage",
            "image_id": "1521359/3bb5bc215c38e44d07e1",
            "title": "Город с башней",
            "description": "Что за город?"
        }
        response["session_state"] = {"stage": "game_started"}
    else:
        response["response"]["text"] = "Жаль! Если передумаешь, просто скажи 'давай сыграем'."
        response["response"]["tts"] = "Жаль! Если передумаешь, просто скажи 'давай сыграем'."
        response["session_state"] = {"stage": "initial"}

    return jsonify(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

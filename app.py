from flask import Flask, request, jsonify


app = Flask(__name__)


@app.route('/alice', methods=['POST'])
def alice_skill():
    req = request.get_json()
    user_message = req.get("request", {}).get("original_utterance", "").lower()

    if not user_message:
        response = {
            "response": {
                "text": "Привет! Давай сыграем в игру? Попробуй отгадать город по фото. Согласен?",
                "tts": "Привет! Давай сыграем в игру? Попробуй отгадать город по фото. Согласен?",
                "buttons": [
                    {"title": "Да", "hide": True},
                    {"title": "Нет", "hide": True}
                ],
                "end_session": False
            },
            "session": {
                "session_id": req["session"]["session_id"],
                "message_id": req["session"]["message_id"],
                "user_id": req["session"]["user_id"]
            },
            "version": "1.0"
        }
    elif "да" in user_message:
        response = {
            "response": {
                "text": "Отлично! Вот фото города. Отгадай, что это за город?",
                "tts": "Отлично! Вот фото города. Отгадай, что это за город?",
                "card": {
                    "type": "BigImage",
                    "image_id": "1521359/3bb5bc215c38e44d07e1",
                    "title": "Город с башней",
                    "description": "Что за город?"
                },
                "end_session": False
            },
            "session": {
                "session_id": req["session"]["session_id"],
                "message_id": req["session"]["message_id"],
                "user_id": req["session"]["user_id"]
            },
            "version": "1.0"
        }
    else:
        response = {
            "response": {
                "text": "Жаль! Если передумаешь, просто скажи 'давай сыграем'.",
                "tts": "Жаль! Если передумаешь, просто скажи 'давай сыграем'.",
                "end_session": False
            },
            "session": {
                "session_id": req["session"]["session_id"],
                "message_id": req["session"]["message_id"],
                "user_id": req["session"]["user_id"]
            },
            "version": "1.0"
        }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
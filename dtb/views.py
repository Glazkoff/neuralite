import json
import logging
import requests
from django.views import View
from django.http import JsonResponse
from telegram import Update

from dtb.celery import app
from dtb.settings import DEBUG
from tgbot.dispatcher import dispatcher
from tgbot.main import bot

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)


def index(request):
    return JsonResponse({"error": "sup hacker"})


def test(request):
    url = "http://dtb.llm-api:8001/tasks/"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return JsonResponse(
                {"message": "Error sending request to the other container."}, status=500
            )

        # Convert bytes to a JSON-serializable dictionary
        result_data = json.loads(response.content)

        return JsonResponse(
            {"message": "Request sent successfully.", "result": result_data}
        )
    except requests.exceptions.RequestException as e:
        return JsonResponse({"message": f"Error: {e}"}, status=500)


def test2(request):
    url = "http://dtb.llm-api:8001/tasks/"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            url,
            json={
                "text": "Когда человек сознательно или интуитивно выбирает себе в жизни какую-то цель, жизненную задачу, он невольно дает себе оценку. По тому, ради чего человек живет, можно судить и о его самооценке - низкой или высокой. Если человек живет, чтобы приносить людям добро, облегчать их страдания, давать людям радость, то он оценивает себя на уровне этой своей человечности. Он ставит себе цель, достойную человека. Только такая цель позволяет человеку прожить свою жизнь с достоинством и получить настоящую радость. Да, радость! Подумайте: если человек ставит себе задачей увеличивать в жизни добро, приносить людям счастье, какие неудачи могут его постигнуть? Не тому помочь? Но много ли людей не нуждаются в помощи? Если жить только для себя, своими мелкими заботами о собственном благополучии, то от прожитого не останется и следа. Если же жить для других, то другие сберегут то, чему служил, чему отдавал силы. Можно по-разному определять цель своего существования, но цель должна быть. Надо иметь и принципы в жизни. Одно правило в жизни должно быть у каждого человека, в его цели жизни, в его принципах жизни, в его поведении: надо прожить жизнь с достоинством, чтобы не стыдно было вспоминать."
            },
            headers=headers,
        )

        try:
            # Convert bytes to a JSON-serializable dictionary
            result_data = json.loads(response.content)

            return JsonResponse(
                {
                    "message": "Request sent successfully.",
                    "code": response.status_code,
                    "result": result_data,
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "e": str(e),
                    "code": response.status_code,
                }
            )

    except requests.exceptions.RequestException as e:
        return JsonResponse({"message": f"Error: {e}"}, status=500)


class TelegramBotWebhookView(View):
    # WARNING: if fail - Telegram webhook will be delivered again.
    # Can be fixed with async celery task execution
    def post(self, request, *args, **kwargs):
        if DEBUG:
            process_telegram_event(json.loads(request.body))
        else:
            # Process Telegram event in Celery worker (async)
            # Don't forget to run it and & Redis (message broker for Celery)!
            # Locally, You can run all of these services via docker-compose.yml
            process_telegram_event.delay(json.loads(request.body))

        # e.g. remove buttons, typing event
        return JsonResponse({"ok": "POST request processed"})

    def get(self, request, *args, **kwargs):  # for debug
        return JsonResponse({"ok": "Get request received! But nothing done"})

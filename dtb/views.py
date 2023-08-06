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
    url = "http://llm-api:80/tasks/"
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

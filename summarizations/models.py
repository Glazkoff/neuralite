from django.db import models
from users.models import User
from utils.models import CreateUpdateTracker


class SummarizationTask(CreateUpdateTracker):
    telegram_msg_id = models.PositiveBigIntegerField("ID сообщения в Telegram")
    user = models.ForeignKey(
        User, verbose_name="Пользователь Telegram", on_delete=models.CASCADE
    )
    input_text = models.TextField("Отправленный текст")
    openai_summarized_text = models.TextField(
        "Текст суммаризации (OpenAI API)", blank=True
    )
    done = models.BooleanField("Задача по суммаризации завершена", default=False)

    def __str__(self):
        return f"Задача суммаризации #{self.pk}"

    class Meta:
        verbose_name = "Задача суммаризации"
        verbose_name_plural = "Задачи суммаризации"

from django.db import models
from users.models import User
from utils.models import CreateUpdateTracker


class SummarizationTask(CreateUpdateTracker):
    user_telegram_msg_id = models.PositiveBigIntegerField("ID сообщения пользователя")
    bot_telegram_msg_id = models.PositiveBigIntegerField("ID сообщения бота", null=True)
    user = models.ForeignKey(
        User, verbose_name="Пользователь Telegram", on_delete=models.CASCADE
    )
    input_text = models.TextField("Отправленный текст")
    openai_summarized_text = models.TextField(
        "Текст суммаризации (OpenAI API)", blank=True
    )
    last_queue_task_id = models.CharField(max_length=50, blank=True)
    done = models.BooleanField("Задача завершена", default=False)

    def __str__(self):
        return f"Задача суммаризации #{self.pk}"

    class Meta:
        verbose_name = "Задача суммаризации"
        verbose_name_plural = "Задачи суммаризации"

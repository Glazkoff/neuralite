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
    last_queue_task_id = models.CharField(
        "ID главной задачи в очереди", max_length=50, blank=True
    )
    done = models.BooleanField("Задача завершена полностью", default=False)

    def __str__(self):
        return f"Задача суммаризации #{self.pk}"

    class Meta:
        verbose_name = "Задача суммаризации"
        verbose_name_plural = "Задачи суммаризации"
        ordering = ["-created_at"]


class VoiceMessage(CreateUpdateTracker):
    user_telegram_msg_id = models.PositiveBigIntegerField("ID сообщения пользователя")
    bot_telegram_msg_id = models.PositiveBigIntegerField("ID сообщения бота", null=True)
    user = models.ForeignKey(
        User, verbose_name="Пользователь Telegram", on_delete=models.CASCADE
    )
    file_id = models.CharField("ID файла", max_length=255, blank=True)
    duration = models.IntegerField("Длительность (секунд)", null=True, blank=True)
    voice_path = models.CharField("URL файла сообщения", max_length=255, blank=True)
    S3_path = models.CharField("Путь для S3 хранилища", max_length=255, blank=True)
    transcribed_text = models.TextField("Транскрибированный текст", blank=True)
    transcribed = models.BooleanField(
        "Сообщение транскрибировано", default=False, blank=True
    )
    summarization_task = models.ForeignKey(
        SummarizationTask,
        verbose_name="Задача на суммаризацию",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Голосовое сообщение #{self.pk}"

    class Meta:
        verbose_name = "Голосовое сообщение"
        verbose_name_plural = "Голосовые сообщения"

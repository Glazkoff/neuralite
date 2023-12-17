from .models import SummarizationTask, VoiceMessage, LangchainSummarizationTask
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks.langchain_summarization import master_lc_summarization_task
from .tasks.summarization import master_summarization_task
from .tasks.voice import master_voice_message_task


@receiver(post_save, sender=SummarizationTask)
def handle_task_creation(sender, instance: SummarizationTask, created: bool, **kwargs):
    print(f"DEBUG - Task created - #{instance.pk}")
    if not created:
        return

    celery_task = master_summarization_task.delay(instance.pk)
    instance.last_queue_task_id = celery_task.id
    instance.save()


@receiver(post_save, sender=LangchainSummarizationTask)
def handle_task_creation(sender, instance: SummarizationTask, created: bool, **kwargs):
    print(f"DEBUG - Task created - #{instance.pk}")
    if not created:
        return

    celery_task = master_lc_summarization_task.delay(instance.pk)
    instance.last_queue_task_id = celery_task.id
    instance.save()


@receiver(post_save, sender=VoiceMessage)
def handle_voice_message_creation(
    sender, instance: VoiceMessage, created: bool, **kwargs
):
    print(f"DEBUG - VM registered - #{instance.pk}")
    if not created:
        return

    celery_task = master_voice_message_task.delay(instance.pk)
    instance.last_queue_task_id = celery_task.id
    instance.save()

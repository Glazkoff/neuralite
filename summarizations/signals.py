from .models import SummarizationTask
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import call_summarization_api


@receiver(post_save, sender=SummarizationTask)
def handle_task_creation(sender, instance: SummarizationTask, created: bool, **kwargs):
    print(f"DEBUG - Task created - #{instance.pk}")
    if not created:
        return

    celery_task = call_summarization_api.delay(instance.pk)
    instance.last_queue_task_id = celery_task.id
    instance.save()

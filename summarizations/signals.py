from .models import SummarizationTask
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import master_summarization_task


@receiver(post_save, sender=SummarizationTask)
def handle_task_creation(sender, instance: SummarizationTask, created: bool, **kwargs):
    print(f"DEBUG - Task created - #{instance.pk}")
    if not created:
        return

    celery_task = master_summarization_task.delay(instance.pk)
    instance.last_queue_task_id = celery_task.id
    instance.save()

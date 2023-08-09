from django.contrib import admin
from .models import SummarizationTask


@admin.register(SummarizationTask)
class SummarizationTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "user_telegram_msg_id", "created_at", "done")
    list_filter = ("created_at", "done")
    readonly_fields = ("created_at", "updated_at")

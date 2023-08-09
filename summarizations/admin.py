from django.contrib import admin
from .models import SummarizationTask


@admin.register(SummarizationTask)
class SummarizationTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "telegram_msg_id", "created_at")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")

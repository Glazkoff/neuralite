from django.contrib import admin
from .models import SummarizationTask, VoiceMessage, LangchainSummarizationTask


@admin.register(SummarizationTask)
class SummarizationTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "done", "user", "user_telegram_msg_id", "created_at")
    list_filter = ("created_at", "done")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("__str__", "id")


@admin.register(LangchainSummarizationTask)
class LangchainSummarizationTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "done", "user", "user_telegram_msg_id", "created_at")
    list_filter = ("created_at", "done")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("__str__", "id")


@admin.register(VoiceMessage)
class VoiceMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "transcribed", "user", "user_telegram_msg_id", "created_at")
    list_filter = ("created_at", "transcribed")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("summarization_task",)

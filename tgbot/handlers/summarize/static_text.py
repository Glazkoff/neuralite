summ_command = "/summ"
summ_wrong_format = (
    f"Чтобы отправить текст на суммаризацию, "
    f"введите команду {summ_command} с текстом, отделённым пробелом.\n"
)
please_wait = (
    "Номер вашего обращения - {task_id}\nПожалуйста, ожидайте суммаризацию... ⏳"
)
please_wait_voice = (
    "Происходит распознавание голоса (#{voice_message_id})\nПожалуйста, ожидайте... ⏳"
)
message_transcribe = (
    "<b>Транскрибация сообщения #{voice_message_id}</b>\n—\n{transcribed_text}"
)
message_summary = "<b>Суммаризация сообщения #{summarization_task_id}</b>\n—\n{summarized_text}\n\n<b>Извлечённые факты:</b>\n—\n{extracted_facts}"

broadcast_command = "/broadcast"
broadcast_no_access = "Извините, у вас нет доступа к этой функции."
broadcast_wrong_format = (
    f"Чтобы отправить сообщение всем вашим пользователям, "
    f"введите команду {broadcast_command} с текстом, разделенным пробелами.\n"
    f"Например:\n"
    f"{broadcast_command} Привет, мои пользователи! Этот <b>жирный текст</b> для вас, "
    f"а также этот <i>курсивный текст.</i>\n\n"
    f'Примеры использования стиля <code>HTML</code> вы можете найти <a href="https://core.telegram.org/bots/api#html-style">здесь</a>.'
)
confirm_broadcast = "Подтвердить ✅"
decline_broadcast = "Отклонить ❌"
message_is_sent = "Сообщение отправлено ✅"
declined_message_broadcasting = "Рассылка сообщений отклонена ❌"
error_with_html = (
    "Не удается обработать ваш текст со стилем <code>HTML</code>. Причина: \n{reason}"
)

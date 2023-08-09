command_start = "/stats"
only_for_admins = 'Извините, эта функция доступна только администраторам. Установите флаг "admin" в панели администратора.'

secret_admin_commands = (
    "⚠️ Секретные команды для администраторов\n",
    f"{command_start} - статистика бота",
)

users_amount_stat = (
    "<i>Статистика</i>\n"
    + "<b>Пользователей всего</b>: {user_count}\n"
    + "<b>Активных за 24 часа</b>: {active_24}"
)
reply_command = "/reply"
reply_wrong_format = (
    f"Чтобы отправить тестовый ответ на сообщение,"
    f"введите команду {reply_command} с ID сообщения, отделённым пробелом.\n"
)
reply_test = "Отправленный ответ на сообщение с ID #{message_id}"
reply_incorrect_command = "Некорректное ID сообщения"
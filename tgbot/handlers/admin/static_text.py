command_start = "/stats"
only_for_admins = 'Извините, эта функция доступна только администраторам. Установите флаг "admin" в панели администратора Django.'

secret_admin_commands = (
    "⚠️ Секретные команды для администраторов\n",
    f"{command_start} - статистика бота",
)

users_amount_stat = (
    "<i>Статистика</i>\n"
    + "<b>Пользователей всего</b>: {user_count}\n"
    + "<b>Активных за 24 часа</b>: {active_24}"
)

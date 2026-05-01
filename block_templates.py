# -*- coding: utf-8 -*-
STEP_TEMPLATES = {
    # Отправка
    "📨 Отправить в ЛС": {
        "type": "send_ls", "target": "", "text": "", "media": ""
    },
    "📢 Отправить в чат": {
        "type": "send_chat", "target": "", "text": "", "media": ""
    },
    "💬 Комментарий в канал": {
        "type": "comment", "target": "", "text": "", "media": ""
    },
    "🤖 Команда боту": {
        "type": "bot_command", "target": "", "command": ""
    },
    "📋 Отправить по списку": {
        "type": "send_to_list", "list_file": "", "text": ""
    },
    "🔄 Переслать сообщение": {
        "type": "forward", "from_chat": "", "msg_id": 0, "to_chat": ""
    },
    "📌 Закрепить сообщение": {
        "type": "pin", "target": "", "msg_id": 0
    },
    "🗑️ Удалить сообщение": {
        "type": "delete", "target": "", "msg_id": 0
    },
    "✏️ Редактировать сообщение": {
        "type": "edit", "target": "", "msg_id": 0, "new_text": ""
    },
    "📎 Отправить файл": {
        "type": "send_file", "target": "", "file_path": "", "caption": ""
    },
    "🖼️ Отправить фото": {
        "type": "send_photo", "target": "", "photo_path": "", "caption": ""
    },
    "🎥 Отправить видео": {
        "type": "send_video", "target": "", "video_path": "", "caption": ""
    },
    "🎵 Отправить аудио": {
        "type": "send_audio", "target": "", "audio_path": "", "caption": ""
    },
    "📞 Позвонить": {
        "type": "call", "target": "", "duration": 10
    },
    "📧 Отправить голосовое": {
        "type": "send_voice", "target": "", "voice_path": ""
    },

    # Реакции
    "🔥 Реакция на пост": {
        "type": "reaction", "target": "", "msg_id": 0, "emoji": "👍"
    },
    "❤️ Лайк посту": {
        "type": "reaction", "target": "", "msg_id": 0, "emoji": "❤"
    },
    "👎 Дизлайк": {
        "type": "reaction", "target": "", "msg_id": 0, "emoji": "👎"
    },
    "🎉 Поздравить": {
        "type": "reaction", "target": "", "msg_id": 0, "emoji": "🎉"
    },
    "💩 Обосрать": {
        "type": "reaction", "target": "", "msg_id": 0, "emoji": "💩"
    },
    "🔥🔥 Много реакций": {
        "type": "multi_reaction", "target": "", "msg_id": 0,
        "emojis": ["👍", "❤", "🔥"]
    },
    "👀 Просмотреть пост": {
        "type": "view", "target": "", "msg_id": 0
    },

    # Подписки
    "🚪 Вступить в чат": {
        "type": "join_chat", "target": ""
    },
    "📋 Подписаться на канал": {
        "type": "subscribe", "target": ""
    },
    "🏃 Выйти из чата": {
        "type": "leave", "target": ""
    },
    "🚫 Заблокировать юзера": {
        "type": "block", "target": ""
    },
    "✅ Разблокировать юзера": {
        "type": "unblock", "target": ""
    },
    "📝 Подать заявку в чат": {
        "type": "join_request", "target": "", "text": ""
    },
    "🔗 Принять инвайт": {
        "type": "accept_invite", "target": ""
    },
    "🔕 Замутить чат": {
        "type": "mute", "target": "", "duration": 0
    },
    "🔔 Размутить чат": {
        "type": "unmute", "target": ""
    },
    "📌 Закрепить чат": {
        "type": "pin_chat", "target": ""
    },
    "📂 Архивировать чат": {
        "type": "archive", "target": ""
    },

    # Кнопки и конкурсы
    "🔘 Нажать кнопку по тексту": {
        "type": "click_button_text", "target": "", "button_text": ""
    },
    "🔘 Нажать кнопку по номеру": {
        "type": "click_button_index", "target": "", "row": 0, "col": 0
    },
    "🔘 Нажать ВСЕ кнопки": {
        "type": "click_all_buttons", "target": ""
    },
    "🔘 Нажать случайную кнопку": {
        "type": "click_random_button", "target": ""
    },
    "🔘 Ждать кнопку и нажать": {
        "type": "wait_button_click", "target": "", "button_text": "", "timeout": 30
    },
    "🔘 Участвовать в конкурсе": {
        "type": "contest_click", "target": "", "button_text": ""
    },
    "🔘 Прожать все конкурсы": {
        "type": "click_all_contests", "target": ""
    },
    "🔘 Ответить на викторину": {
        "type": "quiz_answer", "target": "", "answer_text": ""
    },
    "🔘 Собрать бонус": {
        "type": "collect_bonus", "target": "", "bonus_text": "бонус"
    },

    # Профиль
    "👤 Сменить имя": {
        "type": "set_name", "first_name": "", "last_name": ""
    },
    "📝 Сменить био": {
        "type": "set_bio", "bio": ""
    },
    "🖼️ Сменить аватарку": {
        "type": "set_avatar", "photo_path": ""
    },
    "🔐 Включить 2FA": {
        "type": "enable_2fa", "password": ""
    },
    "🔓 Выключить 2FA": {
        "type": "disable_2fa", "password": ""
    },
    "👻 Скрыть номер": {
        "type": "hide_phone", "hide": True
    },
    "👁️ Скрыть онлайн": {
        "type": "hide_online", "hide": True
    },
    "📛 Сменить username": {
        "type": "set_username", "username": ""
    },

    # Паузы
    "⏰ Пауза (сек)": {
        "type": "sleep", "seconds_from": 1, "seconds_to": 5
    },
    "🕐 Пауза (мин)": {
        "type": "sleep_minutes", "minutes_from": 1, "minutes_to": 5
    },
    "📅 Ждать до времени": {
        "type": "wait_until", "hour": 12, "minute": 0
    },
    "🎲 Случайная пауза": {
        "type": "random_sleep", "min_sec": 10, "max_sec": 300
    },
    "⏱️ Таймер с действием": {
        "type": "timer", "seconds": 60, "action": {}
    },

    # Логика
    "🔁 Повторить N раз": {
        "type": "repeat", "times": 1, "steps": []
    },
    "🔁 Пока не ответит": {
        "type": "repeat_until_reply", "target": "", "steps": []
    },
    "❓ Если-То-Иначе": {
        "type": "if_then", "condition": "", "then": [], "else": []
    },
    "🔀 Случайный выбор": {
        "type": "random_choice", "options": []
    },
    "🔢 Случайное число действий": {
        "type": "random_count", "min": 1, "max": 5, "step": {}
    },
    "📊 По очереди из списка": {
        "type": "iterate_list", "list_file": "", "step_template": {}
    },

    # Капча
    "🧩 Решить капчу (Qwen)": {
        "type": "solve_captcha", "bot": "", "max_retries": 2
    },
    "🧩 Капча (ручной ввод)": {
        "type": "captcha_manual", "bot": ""
    },
    "🤖 Ждать ответа бота": {
        "type": "wait_bot_reply", "bot": "", "expected": "", "timeout": 30
    },
    "🤖 Проверить ответ бота": {
        "type": "check_bot_reply", "bot": "", "expected": ""
    },

    # Голосования
    "📊 Голосовать в опросе": {
        "type": "vote", "target": "", "msg_id": 0, "option": 0
    },
    "📊 Создать опрос": {
        "type": "create_poll", "target": "", "question": "", "options": []
    },
    "📊 Закрыть опрос": {
        "type": "close_poll", "target": "", "msg_id": 0
    },

    # Групповые
    "👥 Добавить в чат": {
        "type": "add_to_chat", "target": "", "users": []
    },
    "👥 Кикнуть из чата": {
        "type": "kick_from_chat", "target": "", "user": ""
    },
    "👥 Создать группу": {
        "type": "create_group", "title": "", "users": []
    },
    "👥 Создать канал": {
        "type": "create_channel", "title": "", "about": ""
    },
    "👥 Сделать админом": {
        "type": "promote_admin", "target": "", "user": ""
    },

    # Сбор информации
    "📥 Скачать медиа": {
        "type": "download_media", "target": "", "msg_id": 0, "save_to": ""
    },
    "📥 Собрать участников": {
        "type": "get_members", "target": "", "save_to": "members.txt"
    },
    "📥 Собрать сообщения": {
        "type": "get_messages", "target": "", "limit": 100,
        "save_to": "messages.txt"
    },
    "📥 Проверить username": {
        "type": "check_username", "username": ""
    },
    "📥 Инфо о чате": {
        "type": "chat_info", "target": ""
    },

    # Уведомления
    "🔔 Уведомить меня": {
        "type": "notify_me", "message": "Готово!"
    },
    "🔔 Лог в файл": {
        "type": "log_to_file", "file": "log.txt", "message": ""
    },
    "🔔 Пауза до команды": {
        "type": "wait_for_command", "command": ""
    },

    # Вебхуки
    "🌐 Webhook (GET)": {
        "type": "webhook_get", "url": ""
    },
    "🌐 Webhook (POST)": {
        "type": "webhook_post", "url": "", "data": {}
    },
    "🌐 Запустить внешний скрипт": {
        "type": "run_script", "command": ""
    },
}


def get_all_block_names():
    return list(STEP_TEMPLATES.keys())


def get_block_template(name):
    template = STEP_TEMPLATES.get(name, {})
    return dict(template)


def search_blocks(query):
    q = query.lower()
    return [name for name in STEP_TEMPLATES if q in name.lower()]

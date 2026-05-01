# -*- coding: utf-8 -*-
import os
import re
import json
import time
import random
import asyncio
import requests
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import (
    ImportChatInviteRequest, CheckChatInviteRequest
)
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.utils import get_display_name

from captcha_solver import CaptchaSolver
from qwen_api import QwenAPI


class StepExecutor:
    def __init__(self, log_callback=None, captcha_callback=None, stop_check=None):
        self.log = log_callback or print
        self.captcha_callback = captcha_callback
        self.stop_check = stop_check or (lambda: False)
        self.solver = None
        self._answer = None
        self._event = None
        self.qwen_api_key = ""

    def set_qwen_key(self, key):
        self.qwen_api_key = key

    def set_answer(self, nums: list):
        self._answer = nums
        if self.solver:
            self.solver.set_answer(nums)
        if self._event:
            self._event.set()

    async def execute_step(self, client, step):
        if self.stop_check():
            return

        t = step.get("type", "")
        try:
            if t == "sleep":
                s = random.randint(
                    step.get("seconds_from", 1),
                    step.get("seconds_to", 5)
                )
                self.log(f"⏰ Пауза {s}с")
                for _ in range(s):
                    if self.stop_check():
                        return
                    await asyncio.sleep(1)

            elif t == "sleep_minutes":
                m = random.randint(
                    step.get("minutes_from", 1),
                    step.get("minutes_to", 5)
                )
                self.log(f"🕐 Пауза {m}мин")
                for _ in range(m * 60):
                    if self.stop_check():
                        return
                    await asyncio.sleep(1)

            elif t == "random_sleep":
                s = random.randint(
                    step.get("min_sec", 10),
                    step.get("max_sec", 300)
                )
                self.log(f"🎲 Случайная пауза {s}с")
                for _ in range(s):
                    if self.stop_check():
                        return
                    await asyncio.sleep(1)

            elif t == "wait_until":
                hour = step.get("hour", 12)
                minute = step.get("minute", 0)
                now = datetime.now()
                target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if target <= now:
                    from datetime import timedelta
                    target += timedelta(days=1)
                wait_sec = (target - now).total_seconds()
                self.log(f"📅 Жду до {hour:02d}:{minute:02d} ({wait_sec:.0f}с)")
                for _ in range(int(wait_sec)):
                    if self.stop_check():
                        return
                    await asyncio.sleep(1)

            elif t == "timer":
                seconds = step.get("seconds", 60)
                action = step.get("action", {})
                self.log(f"⏱️ Таймер {seconds}с")
                await asyncio.sleep(seconds)
                if action and not self.stop_check():
                    await self.execute_step(client, action)

            # === КАПЧА ===
            elif t == "solve_captcha":
                bot = step.get("bot", "")
                if not bot:
                    self.log("❌ Нет бота для капчи")
                    return
                self.solver = CaptchaSolver(
                    client, self.qwen_api_key,
                    log_callback=self.log
                )
                self.solver.need_human_callback = self.captcha_callback
                await self.solver.solve(bot)
                self.solver = None

            elif t == "captcha_manual":
                bot = step.get("bot", "")
                self.log(f"🧩 Жду капчу от @{bot}...")
                try:
                    ev = await client.wait_for(
                        events.NewMessage(from_users=bot, func=lambda e: e.photo),
                        timeout=60
                    )
                    path = await ev.message.download_media()
                    question = ev.message.text or "Решите капчу"
                    if self.captcha_callback:
                        self.captcha_callback(path or "", question, bot)
                    self._answer = None
                    self._event = asyncio.Event()
                    await self._event.wait()
                    if self._answer and ev.message.buttons:
                        await self._click_captcha_buttons(ev.message, self._answer)
                    if path and os.path.exists(path):
                        os.remove(path)
                except asyncio.TimeoutError:
                    self.log("⏰ Капча не появилась")

            # === ОТПРАВКА ===
            elif t == "send_ls":
                target = step.get("target", "")
                text = step.get("text", "")
                if target and text:
                    entity = await client.get_input_entity(target)
                    await client.send_message(entity, text)
                    self.log(f"📨 ЛС → @{target}")

            elif t == "send_chat":
                target = step.get("target", "")
                text = step.get("text", "")
                if target and text:
                    entity = await client.get_input_entity(target)
                    await client.send_message(entity, text)
                    self.log(f"📢 Сообщение в чат {target}")

            elif t == "comment":
                target = step.get("target", "")
                text = step.get("text", "")
                if target and text:
                    entity = await client.get_input_entity(target)
                    await client.send_message(entity, text, comment_to=step.get("msg_id"))
                    self.log(f"💬 Комментарий → {target}")

            elif t == "bot_command":
                target = step.get("target", "")
                command = step.get("command", "")
                if target and command:
                    entity = await client.get_input_entity(target)
                    await client.send_message(entity, command)
                    self.log(f"🤖 {command} → @{target}")

            elif t == "send_to_list":
                list_file = step.get("list_file", "")
                text = step.get("text", "")
                if list_file and text and os.path.exists(list_file):
                    with open(list_file, "r", encoding="utf-8") as f:
                        targets = [line.strip() for line in f if line.strip()]
                    for tg in targets:
                        if self.stop_check():
                            break
                        try:
                            entity = await client.get_input_entity(tg)
                            await client.send_message(entity, text)
                            self.log(f"📋 Отправлено → {tg}")
                            await asyncio.sleep(random.uniform(1, 3))
                        except Exception as ex:
                            self.log(f"❌ {tg}: {ex}")

            elif t == "forward":
                from_chat = step.get("from_chat", "")
                msg_id = step.get("msg_id", 0)
                to_chat = step.get("to_chat", "")
                if from_chat and msg_id and to_chat:
                    from_entity = await client.get_input_entity(from_chat)
                    to_entity = await client.get_input_entity(to_chat)
                    await client.forward_messages(to_entity, msg_id, from_entity)
                    self.log(f"🔄 Переслано {msg_id} → {to_chat}")

            elif t == "pin":
                target = step.get("target", "")
                msg_id = step.get("msg_id", 0)
                if target and msg_id:
                    entity = await client.get_input_entity(target)
                    await client.pin_message(entity, msg_id)
                    self.log(f"📌 Закреплено {msg_id}")

            elif t == "delete":
                target = step.get("target", "")
                msg_id = step.get("msg_id", 0)
                if target and msg_id:
                    entity = await client.get_input_entity(target)
                    await client.delete_messages(entity, msg_id)
                    self.log(f"🗑️ Удалено {msg_id}")

            elif t == "edit":
                target = step.get("target", "")
                msg_id = step.get("msg_id", 0)
                new_text = step.get("new_text", "")
                if target and msg_id and new_text:
                    entity = await client.get_input_entity(target)
                    await client.edit_message(entity, msg_id, new_text)
                    self.log(f"✏️ Отредактировано {msg_id}")

            elif t == "send_file":
                target = step.get("target", "")
                file_path = step.get("file_path", "")
                caption = step.get("caption", "")
                if target and file_path and os.path.exists(file_path):
                    entity = await client.get_input_entity(target)
                    await client.send_file(entity, file_path, caption=caption)
                    self.log(f"📎 Файл → {target}")

            elif t == "send_photo":
                target = step.get("target", "")
                photo_path = step.get("photo_path", "")
                caption = step.get("caption", "")
                if target and photo_path and os.path.exists(photo_path):
                    entity = await client.get_input_entity(target)
                    await client.send_file(entity, photo_path, caption=caption)
                    self.log(f"🖼️ Фото → {target}")

            elif t == "send_video":
                target = step.get("target", "")
                video_path = step.get("video_path", "")
                caption = step.get("caption", "")
                if target and video_path and os.path.exists(video_path):
                    entity = await client.get_input_entity(target)
                    await client.send_file(entity, video_path, caption=caption)
                    self.log(f"🎥 Видео → {target}")

            elif t == "send_audio":
                target = step.get("target", "")
                audio_path = step.get("audio_path", "")
                caption = step.get("caption", "")
                if target and audio_path and os.path.exists(audio_path):
                    entity = await client.get_input_entity(target)
                    await client.send_file(entity, audio_path, caption=caption)
                    self.log(f"🎵 Аудио → {target}")

            elif t == "send_voice":
                target = step.get("target", "")
                voice_path = step.get("voice_path", "")
                if target and voice_path and os.path.exists(voice_path):
                    entity = await client.get_input_entity(target)
                    await client.send_file(entity, voice_path, voice_note=True)
                    self.log(f"📧 Голосовое → {target}")

            elif t == "call":
                target = step.get("target", "")
                duration = step.get("duration", 10)
                if target:
                    entity = await client.get_input_entity(target)
                    call = await client(functions.phone.RequestCallRequest(
                        user_id=entity,
                        random_id=random.randint(0, 2**31 - 1)
                    ))
                    self.log(f"📞 Звонок → @{target}")
                    await asyncio.sleep(duration)
                    try:
                        await call.discard()
                    except:
                        pass

            # === РЕАКЦИИ ===
            elif t == "reaction":
                target = step.get("target", "")
                msg_id = step.get("msg_id", 0)
                emoji = step.get("emoji", "👍")
                if target and msg_id:
                    entity = await client.get_input_entity(target)
                    await client.send_reaction(entity, msg_id, emoji)
                    self.log(f"🔥 Реакция {emoji}")

            elif t == "multi_reaction":
                target = step.get("target", "")
                msg_id = step.get("msg_id", 0)
                emojis = step.get("emojis", ["👍"])
                if target and msg_id:
                    entity = await client.get_input_entity(target)
                    for em in emojis:
                        if self.stop_check():
                            break
                        await client.send_reaction(entity, msg_id, em)
                        await asyncio.sleep(0.2)
                    self.log(f"🔥🔥 {len(emojis)} реакций")

            elif t == "view":
                target = step.get("target", "")
                msg_id = step.get("msg_id", 0)
                if target and msg_id:
                    entity = await client.get_input_entity(target)
                    await client.send_read_acknowledge(entity, max_id=msg_id)
                    self.log(f"👀 Просмотрено {msg_id}")

            # === ПОДПИСКИ ===
            elif t == "join_chat":
                target = step.get("target", "")
                if target:
                    if "t.me/+" in target or "t.me/joinchat/" in target:
                        invite_hash = target.split("/")[-1].replace("+", "")
                        await client(ImportChatInviteRequest(invite_hash))
                    else:
                        entity = await client.get_input_entity(target)
                        await client(JoinChannelRequest(entity))
                    self.log(f"🚪 Вступил: {target}")

            elif t == "subscribe":
                target = step.get("target", "")
                if target:
                    entity = await client.get_input_entity(target)
                    await client(JoinChannelRequest(entity))
                    self.log(f"📋 Подписан: {target}")

            elif t == "leave":
                target = step.get("target", "")
                if target:
                    entity = await client.get_input_entity(target)
                    await client.delete_dialog(entity)
                    self.log(f"🏃 Вышел: {target}")

            elif t == "block":
                target = step.get("target", "")
                if target:
                    entity = await client.get_input_entity(target)
                    await client(BlockRequest(entity))
                    self.log(f"🚫 Заблокирован: {target}")

            elif t == "unblock":
                target = step.get("target", "")
                if target:
                    entity = await client.get_input_entity(target)
                    await client(UnblockRequest(entity))
                    self.log(f"✅ Разблокирован: {target}")

            elif t == "join_request":
                target = step.get("target", "")
                text = step.get("text", "")
                if target:
                    entity = await client.get_input_entity(target)
                    await client(functions.messages.ImportChatInviteRequest(target))
                    self.log(f"📝 Заявка: {target}")

            elif t == "accept_invite":
                target = step.get("target", "")
                if target:
                    invite_hash = target.split("/")[-1].replace("+", "")
                    await client(ImportChatInviteRequest(invite_hash))
                    self.log(f"🔗 Инвайт принят: {target}")

            elif t == "mute":
                target = step.get("target", "")
                duration = step.get("duration", 0)
                if target:
                    entity = await client.get_input_entity(target)
                    await client(functions.account.UpdateNotifySettingsRequest(
                        peer=entity,
                        settings={"mute_until": int(time.time() + duration) if duration else 2147483647}
                    ))
                    self.log(f"🔕 Замучен: {target}")

            elif t == "unmute":
                target = step.get("target", "")
                if target:
                    entity = await client.get_input_entity(target)
                    await client(functions.account.UpdateNotifySettingsRequest(
                        peer=entity,
                        settings={"mute_until": 0}
                    ))
                    self.log(f"🔔 Размучен: {target}")

            elif t == "pin_chat":
                target = step.get("target", "")
                if target:
                    entity = await client.get_input_entity(target)
                    await client(functions.messages.ToggleDialogPinRequest(
                        peer=entity,
                        pinned=True
                    ))
                    self.log(f"📌 Чат закреплён")

            elif t == "archive":
                target = step.get("target", "")
                if target:
                    entity = await client.get_input_entity(target)
                    await client(functions.messages.ToggleDialogPinRequest(
                        peer=entity,
                        pinned=False
                    ))
                    await client(functions.folders.EditPeerFoldersRequest(
                        folder_peers=[entity]
                    ))
                    self.log(f"📂 Архивирован")

            # === КНОПКИ ===
            elif t in (
                "click_button_text", "click_button_index",
                "click_all_buttons", "click_random_button"
            ):
                await self._handle_button_click(client, step, t)

            elif t == "wait_button_click":
                target = step.get("target", "")
                button_text = step.get("button_text", "")
                timeout = step.get("timeout", 30)
                if target and button_text:
                    entity = await client.get_input_entity(target)
                    self.log(f"🔘 Жду кнопку '{button_text}'...")
                    start = time.time()
                    while time.time() - start < timeout:
                        if self.stop_check():
                            return
                        try:
                            messages = await client.get_messages(entity, limit=1)
                            if messages and messages[0].buttons:
                                for row in messages[0].buttons:
                                    for btn in row:
                                        if button_text.lower() in btn.text.lower():
                                            await btn.click()
                                            self.log(f"🔘 Нажато: {btn.text}")
                                            return
                        except:
                            pass
                        await asyncio.sleep(2)
                    self.log("⏰ Кнопка не появилась")

            elif t == "contest_click":
                target = step.get("target", "")
                button_text = step.get("button_text", "")
                if target:
                    entity = await client.get_input_entity(target)
                    messages = await client.get_messages(entity, limit=5)
                    for msg in messages:
                        if msg.buttons:
                            for row in msg.buttons:
                                for btn in row:
                                    search_text = button_text or "участвую"
                                    if search_text.lower() in btn.text.lower():
                                        await btn.click()
                                        self.log(f"🏆 Конкурс: {btn.text}")
                                        return

            elif t == "click_all_contests":
                target = step.get("target", "")
                if target:
                    entity = await client.get_input_entity(target)
                    messages = await client.get_messages(entity, limit=10)
                    for msg in messages:
                        if msg.buttons:
                            for row in msg.buttons:
                                for btn in row:
                                    if any(txt in btn.text.lower() for txt in (
                                        "участвую", "участвовать", "принять участие",
                                        "хочу", "иду", "буду", "🔥"
                                    )):
                                        self.log(f"🏆 {btn.text}")
                                        await btn.click()
                                        await asyncio.sleep(0.5)

            elif t == "quiz_answer":
                target = step.get("target", "")
                answer_text = step.get("answer_text", "")
                if target and answer_text:
                    entity = await client.get_input_entity(target)
                    messages = await client.get_messages(entity, limit=3)
                    for msg in messages:
                        if msg.buttons:
                            for row in msg.buttons:
                                for btn in row:
                                    if answer_text.lower() in btn.text.lower():
                                        await btn.click()
                                        self.log(f"🎯 Викторина: {btn.text}")
                                        return

            elif t == "collect_bonus":
                target = step.get("target", "")
                bonus_text = step.get("bonus_text", "бонус")
                if target:
                    entity = await client.get_input_entity(target)
                    messages = await client.get_messages(entity, limit=5)
                    for msg in messages:
                        if msg.buttons:
                            for row in msg.buttons:
                                for btn in row:
                                    if bonus_text.lower() in btn.text.lower():
                                        await btn.click()
                                        self.log(f"🎁 Бонус: {btn.text}")
                                        return

            # === ПРОФИЛЬ ===
            elif t == "set_name":
                first = step.get("first_name", "")
                last = step.get("last_name", "")
                if first:
                    await client(UpdateProfileRequest(first_name=first, last_name=last))
                    self.log(f"👤 Имя: {first} {last}")

            elif t == "set_bio":
                bio = step.get("bio", "")
                if bio:
                    await client(UpdateProfileRequest(about=bio))
                    self.log("📝 Био обновлено")

            elif t == "set_avatar":
                path = step.get("photo_path", "")
                if path and os.path.exists(path):
                    up = await client.upload_file(path)
                    await client(UploadProfilePhotoRequest(up))
                    self.log("🖼️ Аватарка обновлена")

            elif t == "set_username":
                username = step.get("username", "")
                if username:
                    await client(UpdateUsernameRequest(username=username.replace("@", "")))
                    self.log(f"📛 @{username}")

            elif t == "enable_2fa":
                password = step.get("password", "")
                if password:
                    await client.edit_2fa(new_password=password)
                    self.log("🔐 2FA включена")

            elif t == "disable_2fa":
                password = step.get("password", "")
                if password:
                    await client.edit_2fa(current_password=password, new_password=None)
                    self.log("🔓 2FA выключена")

            elif t == "hide_phone":
                hide = step.get("hide", True)
                await client(functions.privacy.SetPrivacyRequest(
                    key="phone_number",
                    rules=[functions.privacy.PrivacyValueDisallowAll()]
                ))
                self.log(f"👻 Номер {'скрыт' if hide else 'показан'}")

            elif t == "hide_online":
                hide = step.get("hide", True)
                await client(functions.privacy.SetPrivacyRequest(
                    key="status",
                    rules=[functions.privacy.PrivacyValueDisallowAll()]
                ))
                self.log(f"👁️ Онлайн {'скрыт' if hide else 'показан'}")

            # === ЛОГИКА ===
            elif t == "repeat":
                times = step.get("times", 1)
                sub_steps = step.get("steps", [])
                for _ in range(times):
                    if self.stop_check():
                        break
                    for sub in sub_steps:
                        if self.stop_check():
                            break
                        await self.execute_step(client, sub)

            elif t == "repeat_until_reply":
                target = step.get("target", "")
                sub_steps = step.get("steps", [])
                if target and sub_steps:
                    entity = await client.get_input_entity(target)
                    while not self.stop_check():
                        messages = await client.get_messages(entity, limit=1)
                        if messages and not messages[0].out:
                            self.log("📩 Получен ответ!")
                            break
                        for sub in sub_steps:
                            if self.stop_check():
                                break
                            await self.execute_step(client, sub)
                        await asyncio.sleep(5)

            elif t == "if_then":
                condition = step.get("condition", "true")
                if condition.lower() == "true":
                    sub = step.get("then", [])
                else:
                    sub = step.get("else", [])
                for s in sub:
                    if self.stop_check():
                        break
                    await self.execute_step(client, s)

            elif t == "random_choice":
                options = step.get("options", [])
                if options:
                    choice = random.choice(options)
                    await self.execute_step(client, choice)

            elif t == "random_count":
                cnt = random.randint(
                    step.get("min", 1),
                    step.get("max", 5)
                )
                sub = step.get("step", {})
                self.log(f"🔢 {cnt} повторений")
                for _ in range(cnt):
                    if self.stop_check():
                        break
                    await self.execute_step(client, sub)

            elif t == "iterate_list":
                list_file = step.get("list_file", "")
                sub_template = step.get("step_template", {})
                if list_file and sub_template and os.path.exists(list_file):
                    with open(list_file, "r", encoding="utf-8") as f:
                        items = [line.strip() for line in f if line.strip()]
                    for item in items:
                        if self.stop_check():
                            break
                        new_step = dict(sub_template)
                        for k, v in new_step.items():
                            if isinstance(v, str):
                                new_step[k] = v.replace("{item}", item)
                        await self.execute_step(client, new_step)

            # === ГОЛОСОВАНИЯ ===
            elif t == "vote":
                target = step.get("target", "")
                msg_id = step.get("msg_id", 0)
                option = step.get("option", 0)
                if target and msg_id:
                    entity = await client.get_input_entity(target)
                    await client(functions.messages.SendVoteRequest(
                        peer=entity,
                        msg_id=msg_id,
                        options=[chr(ord('a') + option)]
                    ))
                    self.log(f"📊 Голос: вариант {option}")

            elif t == "create_poll":
                target = step.get("target", "")
                question = step.get("question", "")
                options = step.get("options", [])
                if target and question and options:
                    entity = await client.get_input_entity(target)
                    await client(functions.messages.SendMediaRequest(
                        peer=entity,
                        media=functions.InputMediaPollRequest(
                            poll=functions.PollRequest(
                                question=question,
                                answers=[functions.PollAnswerRequest(text=opt) for opt in options]
                            )
                        )
                    ))
                    self.log(f"📊 Опрос создан: {question}")

            elif t == "close_poll":
                target = step.get("target", "")
                msg_id = step.get("msg_id", 0)
                if target and msg_id:
                    entity = await client.get_input_entity(target)
                    await client(functions.messages.EditMessageRequest(
                        peer=entity,
                        id=msg_id,
                        media=functions.InputMediaPollRequest(
                            poll=functions.PollRequest(closed=True)
                        )
                    ))
                    self.log("📊 Опрос закрыт")

            # === ГРУППОВЫЕ ===
            elif t == "add_to_chat":
                target = step.get("target", "")
                users = step.get("users", [])
                if target and users:
                    entity = await client.get_input_entity(target)
                    for user in users:
                        user_entity = await client.get_input_entity(user)
                        await client(functions.messages.AddChatUserRequest(
                            chat_id=entity,
                            user_id=user_entity,
                            fwd_limit=0
                        ))
                    self.log(f"👥 Добавлено {len(users)} в {target}")

            elif t == "kick_from_chat":
                target = step.get("target", "")
                user = step.get("user", "")
                if target and user:
                    entity = await client.get_input_entity(target)
                    user_entity = await client.get_input_entity(user)
                    await client(functions.channels.EditBannedRequest(
                        channel=entity,
                        participant=user_entity,
                        banned_rights=functions.ChatBannedRights(
                            until_date=0,
                            view_messages=True
                        )
                    ))
                    self.log(f"👥 Кикнут: {user}")

            elif t == "create_group":
                title = step.get("title", "")
                users = step.get("users", [])
                if title:
                    user_entities = []
                    for user in users:
                        user_entities.append(await client.get_input_entity(user))
                    result = await client(functions.messages.CreateChatRequest(
                        users=user_entities,
                        title=title
                    ))
                    self.log(f"👥 Группа создана: {title}")

            elif t == "create_channel":
                title = step.get("title", "")
                about = step.get("about", "")
                if title:
                    result = await client(functions.channels.CreateChannelRequest(
                        title=title,
                        about=about,
                        broadcast=True
                    ))
                    self.log(f"👥 Канал создан: {title}")

            elif t == "promote_admin":
                target = step.get("target", "")
                user = step.get("user", "")
                if target and user:
                    entity = await client.get_input_entity(target)
                    user_entity = await client.get_input_entity(user)
                    await client(functions.channels.EditAdminRequest(
                        channel=entity,
                        user_id=user_entity,
                        admin_rights=functions.ChatAdminRights(
                            change_info=True,
                            post_messages=True,
                            edit_messages=True,
                            delete_messages=True,
                            ban_users=True,
                            invite_users=True,
                            pin_messages=True,
                            add_admins=True,
                            anonymous=True,
                            manage_call=True,
                            other=True
                        ),
                        rank="Админ"
                    ))
                    self.log(f"👥 Админ: {user}")

            # === СБОР ИНФОРМАЦИИ ===
            elif t == "download_media":
                target = step.get("target", "")
                msg_id = step.get("msg_id", 0)
                save_to = step.get("save_to", "downloads/")
                if target and msg_id:
                    entity = await client.get_input_entity(target)
                    message = await client.get_messages(entity, ids=msg_id)
                    if message and message.media:
                        os.makedirs(save_to, exist_ok=True)
                        path = await message.download_media(file=save_to)
                        self.log(f"📥 Скачано: {path}")

            elif t == "get_members":
                target = step.get("target", "")
                save_to = step.get("save_to", "members.txt")
                if target:
                    entity = await client.get_input_entity(target)
                    participants = await client.get_participants(entity)
                    with open(save_to, "w", encoding="utf-8") as f:
                        for p in participants:
                            f.write(f"{p.id} {p.username or ''} {p.first_name or ''}\n")
                    self.log(f"📥 {len(participants)} участников → {save_to}")

            elif t == "get_messages":
                target = step.get("target", "")
                limit = step.get("limit", 100)
                save_to = step.get("save_to", "messages.txt")
                if target:
                    entity = await client.get_input_entity(target)
                    messages = await client.get_messages(entity, limit=limit)
                    with open(save_to, "w", encoding="utf-8") as f:
                        for m in messages:
                            f.write(f"[{m.date}] {m.sender_id}: {m.text or ''}\n")
                    self.log(f"📥 {len(messages)} сообщений → {save_to}")

            elif t == "check_username":
                username = step.get("username", "")
                if username:
                    try:
                        entity = await client.get_entity(username)
                        self.log(f"📥 @{username}: {get_display_name(entity)} (ID: {entity.id})")
                    except:
                        self.log(f"📥 @{username}: свободен")

            elif t == "chat_info":
                target = step.get("target", "")
                if target:
                    entity = await client.get_entity(target)
                    info = (
                        f"Название: {get_display_name(entity)}\n"
                        f"ID: {entity.id}\n"
                        f"Тип: {type(entity).__name__}"
                    )
                    self.log(f"📥 {info}")

            # === УВЕДОМЛЕНИЯ ===
            elif t == "notify_me":
                self.log(f"🔔 {step.get('message', 'Готово!')}")

            elif t == "log_to_file":
                file = step.get("file", "log.txt")
                msg = step.get("message", "")
                with open(file, "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now()}] {msg}\n")

            elif t == "wait_for_command":
                command = step.get("command", "")
                self.log(f"🔔 Жду команду: {command}")
                self._event = asyncio.Event()
                await self._event.wait()

            # === ВЕБХУКИ ===
            elif t == "webhook_get":
                url = step.get("url", "")
                if url:
                    try:
                        r = requests.get(url, timeout=10)
                        self.log(f"🌐 GET {url}: {r.status_code}")
                    except Exception as e:
                        self.log(f"🌐 GET ошибка: {e}")

            elif t == "webhook_post":
                url = step.get("url", "")
                data = step.get("data", {})
                if url:
                    try:
                        r = requests.post(url, json=data, timeout=10)
                        self.log(f"🌐 POST {url}: {r.status_code}")
                    except Exception as e:
                        self.log(f"🌐 POST ошибка: {e}")

            elif t == "run_script":
                command = step.get("command", "")
                if command:
                    import subprocess
                    subprocess.Popen(command, shell=True)
                    self.log(f"🌐 Скрипт: {command}")

            elif t == "wait_bot_reply":
                bot = step.get("bot", "")
                expected = step.get("expected", "")
                timeout = step.get("timeout", 30)
                if bot:
                    self.log(f"🤖 Жду ответ от @{bot}...")
                    try:
                        ev = await client.wait_for(
                            events.NewMessage(from_users=bot),
                            timeout=timeout
                        )
                        reply_text = ev.message.text or ""
                        if expected and expected.lower() not in reply_text.lower():
                            self.log(f"🤖 Неожиданный ответ: {reply_text[:100]}")
                        else:
                            self.log(f"🤖 Ответ: {reply_text[:100]}")
                    except asyncio.TimeoutError:
                        self.log("🤖 Нет ответа")

            elif t == "check_bot_reply":
                bot = step.get("bot", "")
                expected = step.get("expected", "")
                if bot:
                    entity = await client.get_input_entity(bot)
                    messages = await client.get_messages(entity, limit=1)
                    if messages and expected.lower() in (messages[0].text or "").lower():
                        self.log(f"🤖 Найдено: {expected}")
                    else:
                        self.log("🤖 Не найдено")

            else:
                self.log(f"⚠️ Неизвестный шаг: {t}")

        except FloodWaitError as e:
            self.log(f"⚠️ FloodWait {e.seconds}с")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            self.log(f"❌ Ошибка в шаге {t}: {e}")

    async def _handle_button_click(self, client, step, click_type):
        target = step.get("target", "")
        if not target:
            self.log("❌ Нет цели для кнопок")
            return

        try:
            entity = await client.get_input_entity(target)
            messages = await client.get_messages(entity, limit=1)
            if not messages:
                messages_list = []
                async for msg in client.iter_messages(entity, limit=10):
                    if msg.buttons:
                        messages_list.append(msg)
                        break
                messages = messages_list

            if not messages:
                self.log("❌ Сообщений с кнопками не найдено")
                return

            msg = messages[0] if isinstance(messages, list) else messages
            if not msg.buttons:
                self.log("❌ Кнопок нет")
                return

            clicked = 0

            if click_type == "click_all_buttons":
                for r_idx, btn_row in enumerate(msg.buttons):
                    for c_idx, btn in enumerate(btn_row):
                        if btn.text.lower() not in (
                            "подтвердить", "готово", "отправить",
                            "ok", "submit", "done", "далее", "next", "confirm"
                        ):
                            self.log(f"👆 [{r_idx},{c_idx}] {btn.text}")
                            await btn.click()
                            clicked += 1
                            await asyncio.sleep(0.3)

            elif click_type == "click_random_button":
                all_btns = [
                    (r, c, btn)
                    for r, btn_row in enumerate(msg.buttons)
                    for c, btn in enumerate(btn_row)
                ]
                if all_btns:
                    r, c, btn = random.choice(all_btns)
                    self.log(f"🎲 [{r},{c}] {btn.text}")
                    await btn.click()
                    clicked += 1

            elif click_type == "click_button_text":
                button_text = step.get("button_text", "")
                if button_text:
                    for r_idx, btn_row in enumerate(msg.buttons):
                        for c_idx, btn in enumerate(btn_row):
                            if button_text.lower() in btn.text.lower():
                                self.log(f"👆 [{r_idx},{c_idx}] {btn.text}")
                                await btn.click()
                                clicked += 1
                                await asyncio.sleep(0.2)
                                break
                        if clicked > 0:
                            break

            elif click_type == "click_button_index":
                row = step.get("row", 0)
                col = step.get("col", 0)
                if row < len(msg.buttons) and col < len(msg.buttons[row]):
                    btn = msg.buttons[row][col]
                    self.log(f"👆 [{row},{col}] {btn.text}")
                    await btn.click()
                    clicked += 1

            # Авто-подтверждение
            if clicked > 0:
                for btn_row in msg.buttons:
                    for btn in btn_row:
                        if btn.text.lower() in (
                            "подтвердить", "готово", "отправить",
                            "ok", "submit", "done", "далее", "next", "confirm"
                        ):
                            await btn.click()
                            self.log(f"✅ Подтверждено: {btn.text}")
                            break

        except Exception as e:
            self.log(f"❌ Кнопки: {e}")

    async def _click_captcha_buttons(self, msg, nums):
        if not msg.buttons:
            return False
        clicked = 0
        for row in msg.buttons:
            for btn in row:
                if btn.text.isdigit() and int(btn.text) in nums:
                    await btn.click()
                    clicked += 1
                    await asyncio.sleep(0.3)

        confirm_keywords = (
            "подтвердить", "готово", "отправить", "ok", "submit",
            "done", "далее", "next", "confirm"
        )
        for row in msg.buttons:
            for btn in row:
                if any(k in btn.text.lower() for k in confirm_keywords):
                    await btn.click()
                    break
        return clicked > 0

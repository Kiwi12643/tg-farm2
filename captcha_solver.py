# -*- coding: utf-8 -*-
import os
import re
import asyncio
import base64
from telethon import events
from qwen_api import QwenAPI


class CaptchaSolver:
    def __init__(self, client, qwen_api_key: str, log_callback=None):
        self.client = client
        self.qwen = QwenAPI(qwen_api_key)
        self.retries = 2
        self.stop_flag = False
        self._answer = None
        self._event = None
        self.log = log_callback or print
        self.need_human_callback = None

    async def solve(self, bot_username: str) -> bool:
        for attempt in range(1, self.retries + 1):
            if self.stop_flag:
                return False
            self.log(f"🤖 Попытка {attempt}/{self.retries}")
            if await self._try_once(bot_username):
                self.log("✅ Капча решена!")
                return True
            if attempt < self.retries:
                await asyncio.sleep(2)

        self.log("🆘 Нужен человек!")
        return await self._call_human(bot_username)

    async def _try_once(self, bot: str) -> bool:
        try:
            ev = await self.client.wait_for(
                events.NewMessage(from_users=bot, func=lambda e: e.photo),
                timeout=30
            )
            path = await ev.message.download_media()
            if not path:
                return False

            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            os.remove(path)

            question = ev.message.text or "Выберите подходящие картинки"
            nums = self.qwen.solve_captcha(b64, question)
            if not nums:
                self.log("❌ Qwen не распознала")
                return False

            self.log(f"🎯 Секции: {nums}")
            return await self._click_buttons(ev.message, nums)

        except asyncio.TimeoutError:
            self.log("⏰ Таймаут")
            return False
        except Exception as e:
            self.log(f"❌ {e}")
            return False

    async def _click_buttons(self, msg, nums: list) -> bool:
        if not msg.buttons:
            return False
        clicked = 0
        for row in msg.buttons:
            for btn in row:
                if btn.text.isdigit() and int(btn.text) in nums:
                    self.log(f"👆 Кнопка {btn.text}")
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

    async def _call_human(self, bot: str) -> bool:
        try:
            ev = await self.client.wait_for(
                events.NewMessage(from_users=bot, func=lambda e: e.photo),
                timeout=120
            )
        except asyncio.TimeoutError:
            return False

        path = await ev.message.download_media() if ev.message.photo else None
        question = ev.message.text or "Выберите картинки"

        if self.need_human_callback:
            self.need_human_callback(path or "", question, bot)

        self._event = asyncio.Event()
        await self._event.wait()

        if not self._answer:
            if path and os.path.exists(path):
                os.remove(path)
            return False

        ok = await self._click_buttons(ev.message, self._answer)
        if path and os.path.exists(path):
            os.remove(path)
        return ok

    def set_answer(self, nums: list):
        self._answer = nums
        if self._event:
            self._event.set()

    def stop(self):
        self.stop_flag = True
        if self._event:
            self._event.set()

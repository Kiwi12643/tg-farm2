# -*- coding: utf-8 -*-
import os
import asyncio
from threading import Thread
from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError, FloodWaitError
)
import socks

from config import SESSIONS_DIR


class AuthEngine:
    def __init__(self, api_id: int, api_hash: str, phones: list,
                 proxies: list, log_callback=None, progress_callback=None,
                 ask_code_callback=None, ask_2fa_callback=None,
                 account_callback=None, finished_callback=None):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phones = phones
        self.proxies = proxies
        self.log = log_callback or print
        self.progress = progress_callback or (lambda c, t: None)
        self.ask_code = ask_code_callback or (lambda p: None)
        self.ask_2fa = ask_2fa_callback or (lambda p: None)
        self.account = account_callback or (lambda a: None)
        self.finished = finished_callback or (lambda: None)
        self.stop_flag = False
        self._current_phone = None
        self._code = None
        self._password = None
        self._event = None
        self._thread = None

    def start(self):
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.stop_flag = True
        if self._event:
            self._event.set()

    def provide_code(self, code: str):
        self._code = code
        if self._event:
            self._event.set()

    def provide_password(self, password: str):
        self._password = password
        if self._event:
            self._event.set()

    def _run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._auth_all())
        loop.close()
        self.finished()

    async def _auth_all(self):
        total = len(self.phones)
        self.log(f"🚀 Начинаю авторизацию {total} номеров...")

        for i, phone in enumerate(self.phones):
            if self.stop_flag:
                break

            phone = phone.strip()
            if not phone:
                continue

            self.progress(i + 1, total)

            proxy = self.proxies[i] if i < len(self.proxies) else None
            acc = await self._auth_one(phone, proxy)

            if acc:
                self.account(acc)

            if i < total - 1 and not self.stop_flag:
                await asyncio.sleep(2)

        self.log("✅ Авторизация завершена!")

    async def _auth_one(self, phone: str, proxy: dict = None):
        kw = {}
        if proxy:
            pt = socks.SOCKS5 if proxy.get("type") == "socks5" else socks.HTTP
            kw["proxy"] = (
                pt, proxy["host"], proxy["port"],
                proxy.get("username"), proxy.get("password")
            )

        session_file = os.path.join(
            SESSIONS_DIR, phone.replace("+", "")
        )

        client = TelegramClient(session_file, self.api_id, self.api_hash, **kw)
        try:
            await client.connect()

            if await client.is_user_authorized():
                me = await client.get_me()
                self.log(f"[{phone}] ✅ УЖЕ авторизован как @{me.username or me.first_name}")
                await client.disconnect()
                return {
                    "phone": phone,
                    "username": me.username or "",
                    "first_name": me.first_name or "",
                    "last_name": me.last_name or "",
                    "user_id": me.id,
                    "session": session_file,
                    "group": "Все",
                    "status": "✅ Активен",
                    "proxy": proxy
                }

            self.log(f"[{phone}] 📱 Отправляю код...")
            await client.send_code_request(phone)

            self._current_phone = phone
            self._code = None
            self._password = None
            self._event = asyncio.Event()

            self.ask_code(phone)
            self.log(f"[{phone}] 📩 Ожидаю SMS-код...")

            await self._event.wait()

            if self.stop_flag:
                await client.disconnect()
                return None

            code = self._code
            password = self._password

            if not code:
                self.log(f"[{phone}] ❌ Код не введён")
                await client.disconnect()
                return None

            try:
                await client.sign_in(phone=phone, code=code)
            except SessionPasswordNeededError:
                if not password:
                    self._code = None
                    self._password = None
                    self._event = asyncio.Event()

                    self.ask_2fa(phone)
                    self.log(f"[{phone}] 🔐 Нужен пароль 2FA...")

                    await self._event.wait()

                    if self.stop_flag:
                        await client.disconnect()
                        return None

                    password = self._password

                if password:
                    await client.sign_in(password=password)
                else:
                    self.log(f"[{phone}] ❌ Пароль 2FA не введён")
                    await client.disconnect()
                    return None

            me = await client.get_me()
            self.log(f"[{phone}] ✅ УСПЕШНО @{me.username or me.first_name}")

            await client.disconnect()

            return {
                "phone": phone,
                "username": me.username or "",
                "first_name": me.first_name or "",
                "last_name": me.last_name or "",
                "user_id": me.id,
                "session": session_file,
                "group": "Все",
                "status": "✅ Активен",
                "proxy": proxy
            }

        except FloodWaitError as e:
            self.log(f"[{phone}] ⚠️ FloodWait {e.seconds}с")
            await client.disconnect()
            return None
        except Exception as e:
            self.log(f"[{phone}] ❌ Ошибка: {e}")
            await client.disconnect()
            return None

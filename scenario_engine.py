# -*- coding: utf-8 -*-
import os
import random
import asyncio
from threading import Thread
from telethon import TelegramClient
import socks

from step_executor import StepExecutor


class ScenarioEngine:
    def __init__(self, accounts, steps, config, log_callback=None,
                 progress_callback=None, captcha_callback=None,
                 finished_callback=None):
        self.accounts = accounts
        self.steps = steps
        self.config = config
        self.log = log_callback or print
        self.progress = progress_callback or (lambda c, t: None)
        self.captcha_callback = captcha_callback
        self.finished = finished_callback or (lambda: None)
        self.stop_flag = False
        self.executor = None
        self._thread = None

    def start(self):
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.stop_flag = True
        if self.executor:
            self.executor.solver.stop() if self.executor.solver else None

    def set_answer(self, nums: list):
        if self.executor:
            self.executor.set_answer(nums)

    def _run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._run_all())
        loop.close()
        self.finished()

    async def _run_all(self):
        total = len(self.accounts)
        self.log(f"▶ Запуск сценария: {len(self.steps)} шагов, {total} аккаунтов")

        self.executor = StepExecutor(
            log_callback=self.log,
            captcha_callback=self.captcha_callback,
            stop_check=lambda: self.stop_flag
        )
        self.executor.set_qwen_key(self.config.get("qwen_api_key", ""))

        delay_min = self.config.get("delay_between_accounts_min", 3)
        delay_max = self.config.get("delay_between_accounts_max", 8)

        for i, acc in enumerate(self.accounts):
            if self.stop_flag:
                break

            self.progress(i + 1, total)
            await self._run_account(acc)

            if i < total - 1 and not self.stop_flag:
                s = random.uniform(delay_min, delay_max)
                self.log(f"⏳ Пауза между аккаунтами {s:.1f}с")
                await asyncio.sleep(s)

        self.log("✅ Все аккаунты обработаны!")

    async def _run_account(self, acc):
        kw = {}
        proxy = acc.get("proxy")
        if proxy:
            pt = socks.SOCKS5 if proxy.get("type") == "socks5" else socks.HTTP
            kw["proxy"] = (
                pt, proxy["host"], proxy["port"],
                proxy.get("username"), proxy.get("password")
            )

        client = TelegramClient(
            acc["session"],
            self.config["api_id"],
            self.config["api_hash"],
            **kw
        )

        try:
            await client.connect()

            if not await client.is_user_authorized():
                self.log(f"[{acc.get('phone','?')}] ❌ Не авторизован")
                return

            me = await client.get_me()
            self.log(f"[@{me.username or me.first_name}] ▶ Сценарий")

            for step in self.steps:
                if self.stop_flag:
                    break
                await self.executor.execute_step(client, step)

            self.log(f"[@{me.username or me.first_name}] ✅ Готово")

        except Exception as e:
            self.log(f"[{acc.get('phone','?')}] ❌ {e}")
        finally:
            await client.disconnect()

# -*- coding: utf-8 -*-
import json
import os

CONFIG_FILE = "config.json"
ACCOUNTS_FILE = "accounts.json"
SCENARIOS_FILE = "scenarios.json"
PROXIES_FILE = "proxies.json"
SESSIONS_DIR = "sessions"

DEFAULT_CONFIG = {
    "api_id": 123456,
    "api_hash": "",
    "qwen_api_key": "",
    "sessions_folder": SESSIONS_DIR,
    "delay_between_accounts_min": 3,
    "delay_between_accounts_max": 8,
    "delay_between_steps_min": 1,
    "delay_between_steps_max": 3,
    "parallel_accounts": 5,
    "max_per_hour": 30,
    "max_captcha_retries": 2,
    "captcha_timeout": 30,
    "typing_enabled": True,
    "typo_chance": 0.02,
    "sound_on_human_needed": True,
    "flash_on_human_needed": True,
}


class ConfigManager:
    def __init__(self):
        os.makedirs(SESSIONS_DIR, exist_ok=True)

    def load_json(self, path, default):
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default
        return default

    def save_json(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_config(self):
        return self.load_json(CONFIG_FILE, DEFAULT_CONFIG.copy())

    def save_config(self, config):
        self.save_json(CONFIG_FILE, config)

    def load_accounts(self):
        return self.load_json(ACCOUNTS_FILE, [])

    def save_accounts(self, accounts):
        self.save_json(ACCOUNTS_FILE, accounts)

    def load_proxies(self):
        return self.load_json(PROXIES_FILE, [])

    def save_proxies(self, proxies):
        self.save_json(PROXIES_FILE, proxies)

    def load_scenarios(self):
        return self.load_json(SCENARIOS_FILE, [])

    def save_scenarios(self, scenarios):
        self.save_json(SCENARIOS_FILE, scenarios)

    def save_all(self, config, accounts, proxies, scenarios):
        self.save_config(config)
        self.save_accounts(accounts)
        self.save_proxies(proxies)
        self.save_scenarios(scenarios)

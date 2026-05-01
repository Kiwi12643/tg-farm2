# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivymd.app import MDApp


class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))

        layout.add_widget(MDLabel(
            text='⚙️ НАСТРОЙКИ',
            theme_text_color='Custom',
            text_color=(0.35, 0.65, 1, 1),
            font_style='H5',
            bold=True
        ))

        card = MDCard(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(500),
            elevation=4,
            radius=[16]
        )

        card.add_widget(MDLabel(
            text='ОБЩИЕ НАСТРОЙКИ',
            theme_text_color='Custom',
            text_color=(1, 0.75, 0.3, 1),
            font_style='Subtitle1',
            bold=True
        ))

        # Эмуляция печати
        typing_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        typing_row.add_widget(MDLabel(
            text='Эмуляция печати',
            theme_text_color='Custom',
            text_color=(0.8, 0.8, 0.8, 1)
        ))
        self.typing_check = MDCheckbox(active=True)
        typing_row.add_widget(self.typing_check)
        card.add_widget(typing_row)

        # Шанс опечатки
        card.add_widget(MDLabel(
            text='Шанс опечатки (0-0.1):',
            theme_text_color='Custom',
            text_color=(0.7, 0.7, 0.7, 1),
            font_style='Caption'
        ))
        self.typo_input = MDTextField(
            text='0.02',
            mode='rectangle',
            size_hint_y=None,
            height=dp(40)
        )
        card.add_widget(self.typo_input)

        # Звук
        sound_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        sound_row.add_widget(MDLabel(
            text='Звук при капче',
            theme_text_color='Custom',
            text_color=(0.8, 0.8, 0.8, 1)
        ))
        self.sound_check = MDCheckbox(active=True)
        sound_row.add_widget(self.sound_check)
        card.add_widget(sound_row)

        # Мигание
        flash_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        flash_row.add_widget(MDLabel(
            text='Мигание при капче',
            theme_text_color='Custom',
            text_color=(0.8, 0.8, 0.8, 1)
        ))
        self.flash_check = MDCheckbox(active=True)
        flash_row.add_widget(self.flash_check)
        card.add_widget(flash_row)

        # Макс капча ретраев
        card.add_widget(MDLabel(
            text='Макс попыток капчи:',
            theme_text_color='Custom',
            text_color=(0.7, 0.7, 0.7, 1),
            font_style='Caption'
        ))
        self.captcha_retries = MDTextField(
            text='2',
            mode='rectangle',
            size_hint_y=None,
            height=dp(40)
        )
        card.add_widget(self.captcha_retries)

        # Таймаут капчи
        card.add_widget(MDLabel(
            text='Таймаут капчи (сек):',
            theme_text_color='Custom',
            text_color=(0.7, 0.7, 0.7, 1),
            font_style='Caption'
        ))
        self.captcha_timeout = MDTextField(
            text='30',
            mode='rectangle',
            size_hint_y=None,
            height=dp(40)
        )
        card.add_widget(self.captcha_timeout)

        # Лимит в час
        card.add_widget(MDLabel(
            text='Макс аккаунтов в час:',
            theme_text_color='Custom',
            text_color=(0.7, 0.7, 0.7, 1),
            font_style='Caption'
        ))
        self.max_per_hour = MDTextField(
            text='30',
            mode='rectangle',
            size_hint_y=None,
            height=dp(40)
        )
        card.add_widget(self.max_per_hour)

        layout.add_widget(card)

        btn_save = MDRaisedButton(
            text='💾 СОХРАНИТЬ НАСТРОЙКИ',
            size_hint_y=None,
            height=dp(56),
            md_bg_color=(0.2, 0.5, 0.8, 1)
        )
        btn_save.bind(on_release=self._save_settings)
        layout.add_widget(btn_save)

        self.add_widget(layout)

    def on_enter(self):
        app = MDApp.get_running_app()
        cfg = app.config_data
        self.typing_check.active = cfg.get('typing_enabled', True)
        self.typo_input.text = str(cfg.get('typo_chance', 0.02))
        self.sound_check.active = cfg.get('sound_on_human_needed', True)
        self.flash_check.active = cfg.get('flash_on_human_needed', True)
        self.captcha_retries.text = str(cfg.get('max_captcha_retries', 2))
        self.captcha_timeout.text = str(cfg.get('captcha_timeout', 30))
        self.max_per_hour.text = str(cfg.get('max_per_hour', 30))

    def add_log(self, text):
        MDApp.get_running_app().log(text)

    def _save_settings(self, instance):
        try:
            app = MDApp.get_running_app()
            app.config_data.update({
                'typing_enabled': self.typing_check.active,
                'typo_chance': float(self.typo_input.text),
                'sound_on_human_needed': self.sound_check.active,
                'flash_on_human_needed': self.flash_check.active,
                'max_captcha_retries': int(self.captcha_retries.text),
                'captcha_timeout': int(self.captcha_timeout.text),
                'max_per_hour': int(self.max_per_hour.text),
            })
            app.cfg.save_config(app.config_data)
            self.add_log('💾 Настройки сохранены!')
        except Exception as e:
            self.add_log(f'❌ Ошибка: {e}')

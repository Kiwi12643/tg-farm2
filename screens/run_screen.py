# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.progressbar import MDProgressBar
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.app import MDApp

from scenario_engine import ScenarioEngine
from captcha_dialog import show_captcha_dialog


class RunScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scenario_engine = None

        layout = MDBoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))

        layout.add_widget(MDLabel(
            text='▶ ЗАПУСК СЦЕНАРИЯ',
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
            height=dp(300),
            elevation=4,
            radius=[16]
        )

        card.add_widget(MDLabel(
            text='НАСТРОЙКИ ЗАПУСКА',
            theme_text_color='Custom',
            text_color=(1, 0.75, 0.3, 1),
            font_style='Subtitle1',
            bold=True
        ))

        card.add_widget(MDLabel(
            text='Перед запуском:\n1. Авторизуй аккаунты\n2. Создай сценарий в Конструкторе',
            theme_text_color='Custom',
            text_color=(0.7, 0.7, 0.7, 1),
            font_style='Body2',
            size_hint_y=None,
            height=dp(60)
        ))

        card.add_widget(MDLabel(
            text='Задержка между аккаунтами (сек):',
            theme_text_color='Custom',
            text_color=(0.7, 0.7, 0.7, 1),
            font_style='Caption'
        ))

        delay_row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48)
        )

        self.delay_min = MDTextField(
            text='3',
            mode='rectangle',
            hint_text='Мин',
            size_hint_x=0.5,
            size_hint_y=None,
            height=dp(48)
        )
        delay_row.add_widget(self.delay_min)

        self.delay_max = MDTextField(
            text='8',
            mode='rectangle',
            hint_text='Макс',
            size_hint_x=0.5,
            size_hint_y=None,
            height=dp(48)
        )
        delay_row.add_widget(self.delay_max)

        card.add_widget(delay_row)

        # Статус
        self.status_label = MDLabel(
            text='Готов к запуску',
            theme_text_color='Custom',
            text_color=(0.5, 0.8, 0.5, 1),
            font_style='Body1',
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(self.status_label)

        layout.add_widget(card)

        # Прогресс
        self.progress_bar = MDProgressBar(
            size_hint_y=None,
            height=dp(6),
            value=0,
            max=100
        )
        layout.add_widget(self.progress_bar)

        # Кнопки
        btn_row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(56)
        )

        self.btn_run = MDRaisedButton(
            text='▶▶▶ ЗАПУСТИТЬ ◀◀◀',
            size_hint_x=0.7,
            md_bg_color=(0, 0.55, 0, 1),
            font_style='Button'
        )
        self.btn_run.bind(on_release=self._run_scenario)
        btn_row.add_widget(self.btn_run)

        self.btn_stop = MDFlatButton(
            text='⏹ СТОП',
            size_hint_x=0.3,
            theme_text_color='Custom',
            text_color=(1, 0.3, 0.3, 1),
            disabled=True
        )
        self.btn_stop.bind(on_release=self._stop_scenario)
        btn_row.add_widget(self.btn_stop)

        layout.add_widget(btn_row)
        self.add_widget(layout)

    def add_log(self, text):
        MDApp.get_running_app().log(text)

    def _run_scenario(self, instance):
        app = MDApp.get_running_app()

        if not app.accounts:
            self.add_log('❌ Нет авторизованных аккаунтов!')
            return

        # Получаем шаги из конструктора
        constructor = app.sm.get_screen('constructor')
        if not hasattr(constructor, 'get_steps'):
            self.add_log('❌ Ошибка конструктора')
            return

        steps = constructor.get_steps()
        if not steps:
            self.add_log('❌ Сценарий пуст! Создай в Конструкторе')
            return

        try:
            delay_min = int(self.delay_min.text)
            delay_max = int(self.delay_max.text)
        except:
            delay_min, delay_max = 3, 8

        app.config_data['delay_between_accounts_min'] = delay_min
        app.config_data['delay_between_accounts_max'] = delay_max

        self.btn_run.disabled = True
        self.btn_stop.disabled = False
        self.progress_bar.max = len(app.accounts)
        self.progress_bar.value = 0
        self.status_label.text = '▶ Выполняется...'
        self.status_label.text_color = (0.35, 0.65, 1, 1)

        self.scenario_engine = ScenarioEngine(
            accounts=app.accounts,
            steps=steps,
            config=app.config_data,
            log_callback=self.add_log,
            progress_callback=lambda c, t: (
                setattr(self.progress_bar, 'value', c),
                setattr(self.progress_bar, 'max', t)
            ),
            captcha_callback=self._on_captcha,
            finished_callback=self._on_scenario_done
        )
        app.scenario_engine = self.scenario_engine
        self.scenario_engine.start()

        self.add_log(f'▶ Запущено: {len(steps)} шагов, {len(app.accounts)} аккаунтов')

    def _stop_scenario(self, instance):
        if self.scenario_engine:
            self.scenario_engine.stop()
        self._reset_ui()

    def _on_captcha(self, photo_path, question, bot):
        def callback(nums):
            if self.scenario_engine:
                self.scenario_engine.set_answer(nums)
        Clock.schedule_once(
            lambda dt: show_captcha_dialog(photo_path, question, bot, callback),
            0
        )

    def _on_scenario_done(self):
        Clock.schedule_once(lambda dt: self._reset_ui(), 0)
        self.add_log('✅ Сценарий выполнен!')

    def _reset_ui(self):
        self.btn_run.disabled = False
        self.btn_stop.disabled = True
        self.status_label.text = 'Готов к запуску'
        self.status_label.text_color = (0.5, 0.8, 0.5, 1)
        self.scenario_engine = None
        app = MDApp.get_running_app()
        app.scenario_engine = None

# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.progressbar import MDProgressBar
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import platform

from auth_engine import AuthEngine


class AuthScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_engine = None
        self.pending_phone = None
        self.pending_type = None
        self.phones = []

        layout = MDBoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))

        # Заголовок
        layout.add_widget(MDLabel(
            text='🔐 АВТОРИЗАЦИЯ',
            theme_text_color='Custom',
            text_color=(0.35, 0.65, 1, 1),
            font_style='H5',
            bold=True
        ))

        scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(4))

        # API настройки
        card_api = MDCard(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(280),
            elevation=4,
            radius=[16]
        )
        card_api.add_widget(MDLabel(
            text='🔑 ДАННЫЕ API (my.telegram.org)',
            theme_text_color='Custom',
            text_color=(1, 0.75, 0.3, 1),
            font_style='Subtitle1',
            bold=True
        ))

        self.api_id_input = MDTextField(
            hint_text='API ID',
            mode='rectangle',
            size_hint_y=None,
            height=dp(48)
        )
        card_api.add_widget(self.api_id_input)

        self.api_hash_input = MDTextField(
            hint_text='API Hash',
            mode='rectangle',
            size_hint_y=None,
            height=dp(48)
        )
        card_api.add_widget(self.api_hash_input)

        self.qwen_key_input = MDTextField(
            hint_text='Qwen API Key (опционально)',
            mode='rectangle',
            size_hint_y=None,
            height=dp(48)
        )
        card_api.add_widget(self.qwen_key_input)

        btn_save_api = MDRaisedButton(
            text='💾 СОХРАНИТЬ API',
            size_hint_y=None,
            height=dp(48),
            md_bg_color=(0.2, 0.6, 0.2, 1)
        )
        btn_save_api.bind(on_release=self._save_api)
        card_api.add_widget(btn_save_api)

        content.add_widget(card_api)

        # Номера телефонов
        card_phones = MDCard(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(340),
            elevation=4,
            radius=[16]
        )
        card_phones.add_widget(MDLabel(
            text='📱 НОМЕРА ТЕЛЕФОНОВ',
            theme_text_color='Custom',
            text_color=(1, 0.75, 0.3, 1),
            font_style='Subtitle1',
            bold=True
        ))

        self.phone_input = MDTextField(
            hint_text='+79123456789',
            mode='rectangle',
            size_hint_y=None,
            height=dp(48)
        )
        card_phones.add_widget(self.phone_input)

        btn_row_phones = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48)
        )

        btn_add_phone = MDRaisedButton(
            text='➕',
            size_hint_x=0.3,
            md_bg_color=(0.2, 0.5, 0.8, 1)
        )
        btn_add_phone.bind(on_release=self._add_phone)
        btn_row_phones.add_widget(btn_add_phone)

        btn_clear_phones = MDFlatButton(
            text='ОЧИСТИТЬ',
            size_hint_x=0.7,
            theme_text_color='Custom',
            text_color=(1, 0.4, 0.4, 1)
        )
        btn_clear_phones.bind(on_release=self._clear_phones)
        btn_row_phones.add_widget(btn_clear_phones)

        card_phones.add_widget(btn_row_phones)

        self.phones_label = MDLabel(
            text='Нет номеров',
            theme_text_color='Custom',
            text_color=(0.6, 0.6, 0.6, 1),
            font_style='Body2',
            size_hint_y=None,
            height=dp(80)
        )
        card_phones.add_widget(self.phones_label)

        content.add_widget(card_phones)

        # SMS код
        card_sms = MDCard(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(180),
            elevation=4,
            radius=[16]
        )
        card_sms.add_widget(MDLabel(
            text='📩 SMS-КОД / 2FA',
            theme_text_color='Custom',
            text_color=(1, 0.75, 0.3, 1),
            font_style='Subtitle1',
            bold=True
        ))

        self.sms_phone_label = MDLabel(
            text='Нет активного номера',
            theme_text_color='Custom',
            text_color=(1, 0, 1, 1),
            font_style='Body2'
        )
        card_sms.add_widget(self.sms_phone_label)

        self.sms_code_input = MDTextField(
            hint_text='Введи код',
            mode='rectangle',
            size_hint_y=None,
            height=dp(48)
        )
        card_sms.add_widget(self.sms_code_input)

        btn_send_code = MDRaisedButton(
            text='✅ ОТПРАВИТЬ КОД',
            size_hint_y=None,
            height=dp(48),
            md_bg_color=(0, 0.6, 0, 1)
        )
        btn_send_code.bind(on_release=self._send_code)
        card_sms.add_widget(btn_send_code)

        content.add_widget(card_sms)

        # Кнопки авторизации
        btn_row_auth = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(56)
        )

        self.btn_start_auth = MDRaisedButton(
            text='▶ НАЧАТЬ АВТОРИЗАЦИЮ',
            size_hint_x=0.7,
            md_bg_color=(0, 0.55, 0, 1),
            font_style='Button'
        )
        self.btn_start_auth.bind(on_release=self._start_auth)
        btn_row_auth.add_widget(self.btn_start_auth)

        self.btn_stop_auth = MDFlatButton(
            text='⏹ СТОП',
            size_hint_x=0.3,
            theme_text_color='Custom',
            text_color=(1, 0.3, 0.3, 1),
            disabled=True
        )
        self.btn_stop_auth.bind(on_release=self._stop_auth)
        btn_row_auth.add_widget(self.btn_stop_auth)

        content.add_widget(btn_row_auth)

        # Прогресс
        self.progress_bar = MDProgressBar(
            size_hint_y=None,
            height=dp(6),
            running_value=0
        )
        content.add_widget(self.progress_bar)

        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        app = MDApp.get_running_app()
        cfg = app.config_data
        self.api_id_input.text = str(cfg.get('api_id', ''))
        self.api_hash_input.text = cfg.get('api_hash', '')
        self.qwen_key_input.text = cfg.get('qwen_api_key', '')

    def add_log(self, text):
        MDApp.get_running_app().log(text)

    def _save_api(self, instance):
        try:
            api_id = int(self.api_id_input.text)
            api_hash = self.api_hash_input.text.strip()
            qwen = self.qwen_key_input.text.strip()

            app = MDApp.get_running_app()
            app.config_data['api_id'] = api_id
            app.config_data['api_hash'] = api_hash
            app.config_data['qwen_api_key'] = qwen
            app.cfg.save_config(app.config_data)

            self.add_log('💾 API сохранены!')
        except:
            self.add_log('❌ Проверь API ID')

    def _add_phone(self, instance):
        phone = self.phone_input.text.strip()
        if phone:
            self.phones.append(phone)
            self.phone_input.text = ''
            self._update_phones_label()
            self.add_log(f'📱 Добавлен: {phone}')

    def _clear_phones(self, instance):
        self.phones = []
        self._update_phones_label()
        self.add_log('🗑️ Список номеров очищен')

    def _update_phones_label(self):
        if self.phones:
            self.phones_label.text = '\n'.join(self.phones)
        else:
            self.phones_label.text = 'Нет номеров'

    def _start_auth(self, instance):
        if not self.phones:
            self.add_log('❌ Добавь номера!')
            return

        app = MDApp.get_running_app()
        api_id = app.config_data.get('api_id', 0)
        api_hash = app.config_data.get('api_hash', '')

        if not api_id or not api_hash:
            self.add_log('❌ Сохрани API данные!')
            return

        self.btn_start_auth.disabled = True
        self.btn_stop_auth.disabled = False
        self.progress_bar.max = len(self.phones)
        self.progress_bar.value = 0

        self.auth_engine = AuthEngine(
            api_id=api_id,
            api_hash=api_hash,
            phones=self.phones,
            proxies=app.proxies,
            log_callback=self.add_log,
            progress_callback=lambda c, t: (
                setattr(self.progress_bar, 'value', c),
                setattr(self.progress_bar, 'max', t)
            ),
            ask_code_callback=self._on_code_request,
            ask_2fa_callback=self._on_2fa_request,
            account_callback=self._on_account,
            finished_callback=self._on_auth_done
        )
        app.auth_engine = self.auth_engine
        self.auth_engine.start()

    def _stop_auth(self, instance):
        if self.auth_engine:
            self.auth_engine.stop()
        self._reset_auth_ui()

    def _on_code_request(self, phone):
        self.pending_phone = phone
        self.pending_type = 'sms'
        self.sms_phone_label.text = f'📱 {phone}'
        self.sms_code_input.text = ''
        self.sms_code_input.hint_text = 'Введи SMS-код'
        self.add_log(f'[{phone}] 📩 Жду код...')

    def _on_2fa_request(self, phone):
        self.pending_phone = phone
        self.pending_type = '2fa'
        self.sms_phone_label.text = f'🔐 {phone} (2FA)'
        self.sms_code_input.text = ''
        self.sms_code_input.hint_text = 'Введи пароль 2FA'
        self.add_log(f'[{phone}] 🔐 Нужен пароль 2FA')

    def _send_code(self, instance):
        code = self.sms_code_input.text.strip()
        if not code or not self.auth_engine:
            return

        self.auth_engine.provide_code(code)
        self.auth_engine.provide_password(code)
        self.sms_phone_label.text = 'Нет активного номера'
        self.sms_code_input.text = ''
        self.pending_phone = None
        self.pending_type = None
        self.add_log('✅ Код отправлен на проверку')

    def _on_account(self, account):
        app = MDApp.get_running_app()
        found = False
        for i, a in enumerate(app.accounts):
            if a.get('phone') == account['phone']:
                app.accounts[i] = account
                found = True
                break
        if not found:
            app.accounts.append(account)
        app.cfg.save_accounts(app.accounts)

    def _on_auth_done(self):
        Clock.schedule_once(lambda dt: self._reset_auth_ui(), 0)
        self.add_log('✅ Авторизация завершена!')

    def _reset_auth_ui(self):
        self.btn_start_auth.disabled = False
        self.btn_stop_auth.disabled = True
        self.sms_phone_label.text = 'Нет активного номера'
        self.auth_engine = None
        app = MDApp.get_running_app()
        app.auth_engine = None

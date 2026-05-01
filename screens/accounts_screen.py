# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivymd.app import MDApp


class AccountsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))

        layout.add_widget(MDLabel(
            text='👥 АККАУНТЫ',
            theme_text_color='Custom',
            text_color=(0.35, 0.65, 1, 1),
            font_style='H5',
            bold=True
        ))

        self.accounts_card = MDCard(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(500),
            elevation=4,
            radius=[16]
        )

        scroll = MDScrollView()
        self.accounts_label = MDLabel(
            text='Нет аккаунтов\nЗайди во вкладку АВТОРИЗАЦИЯ',
            theme_text_color='Custom',
            text_color=(0.6, 0.6, 0.6, 1),
            font_style='Body1',
            size_hint_y=None,
            halign='center'
        )
        self.accounts_label.bind(
            texture_size=lambda instance, size:
            setattr(instance, 'height', size[1])
        )
        scroll.add_widget(self.accounts_label)
        self.accounts_card.add_widget(scroll)

        btn_row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48)
        )

        btn_refresh = MDRaisedButton(
            text='🔄',
            size_hint_x=0.25,
            md_bg_color=(0.2, 0.5, 0.8, 1)
        )
        btn_refresh.bind(on_release=self._refresh)
        btn_row.add_widget(btn_refresh)

        btn_clear = MDFlatButton(
            text='🗑️ ОЧИСТИТЬ',
            size_hint_x=0.75,
            theme_text_color='Custom',
            text_color=(1, 0.4, 0.4, 1)
        )
        btn_clear.bind(on_release=self._confirm_clear)
        btn_row.add_widget(btn_clear)

        self.accounts_card.add_widget(btn_row)

        layout.add_widget(self.accounts_card)
        self.add_widget(layout)

    def on_enter(self):
        self._update_display()

    def add_log(self, text):
        MDApp.get_running_app().log(text)

    def _refresh(self, instance):
        self._update_display()
        self.add_log('🔄 Аккаунты обновлены')

    def _confirm_clear(self, instance):
        dlg = MDDialog(
            title='Подтверждение',
            text='Удалить ВСЕ аккаунты?',
            buttons=[
                MDFlatButton(text='ОТМЕНА', on_release=lambda x: dlg.dismiss()),
                MDRaisedButton(
                    text='УДАЛИТЬ',
                    md_bg_color=(0.8, 0.2, 0.2, 1),
                    on_release=lambda x: (self._clear_accounts(), dlg.dismiss())
                )
            ]
        )
        dlg.open()

    def _clear_accounts(self):
        app = MDApp.get_running_app()
        app.accounts = []
        app.cfg.save_accounts(app.accounts)
        self._update_display()
        self.add_log('🗑️ Все аккаунты удалены')

    def _update_display(self):
        app = MDApp.get_running_app()
        accounts = app.accounts

        if accounts:
            lines = []
            for a in accounts:
                phone = a.get('phone', '?')
                username = a.get('username', '')
                status = a.get('status', '')
                lines.append(
                    f"📱 {phone} | @{username} | {status}"
                )
            self.accounts_label.text = '\n\n'.join(lines)
            self.accounts_label.halign = 'left'
        else:
            self.accounts_label.text = 'Нет аккаунтов\nЗайди во вкладку АВТОРИЗАЦИЯ'
            self.accounts_label.halign = 'center'

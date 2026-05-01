# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivymd.app import MDApp


class ProxyScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))

        layout.add_widget(MDLabel(
            text='🌐 ПРОКСИ',
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
            text='Формат: ip:port или ip:port:user:pass',
            theme_text_color='Custom',
            text_color=(0.7, 0.7, 0.7, 1),
            font_style='Caption'
        ))

        self.proxy_input = MDTextField(
            hint_text='1.2.3.4:8080\n5.6.7.8:9050:user:pass',
            mode='rectangle',
            multiline=True,
            size_hint_y=None,
            height=dp(180)
        )
        card.add_widget(self.proxy_input)

        btn_parse = MDRaisedButton(
            text='🔍 РАСПАРСИТЬ И СОХРАНИТЬ',
            size_hint_y=None,
            height=dp(48),
            md_bg_color=(0.2, 0.5, 0.8, 1)
        )
        btn_parse.bind(on_release=self._parse_proxies)
        card.add_widget(btn_parse)

        self.proxy_status = MDLabel(
            text='Прокси не загружены',
            theme_text_color='Custom',
            text_color=(0.5, 0.5, 0.5, 1),
            font_style='Body1'
        )
        card.add_widget(self.proxy_status)

        scroll = MDScrollView()
        self.proxy_list_label = MDLabel(
            text='',
            theme_text_color='Custom',
            text_color=(0.8, 0.8, 0.8, 1),
            font_style='Caption',
            size_hint_y=None
        )
        self.proxy_list_label.bind(
            texture_size=lambda instance, size:
            setattr(instance, 'height', size[1])
        )
        scroll.add_widget(self.proxy_list_label)
        card.add_widget(scroll)

        layout.add_widget(card)
        self.add_widget(layout)

    def on_enter(self):
        app = MDApp.get_running_app()
        self._update_proxy_display(app.proxies)

    def add_log(self, text):
        MDApp.get_running_app().log(text)

    def _parse_proxies(self, instance):
        app = MDApp.get_running_app()
        app.proxies = []
        text = self.proxy_input.text.strip()

        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue

            p = {'raw': line}
            if line.startswith('socks5://'):
                line = line.replace('socks5://', '')
                p['type'] = 'socks5'
            else:
                p['type'] = 'http'

            parts = line.split(':')
            if len(parts) >= 2:
                p['host'] = parts[0]
                p['port'] = int(parts[1])
            if len(parts) >= 4:
                p['username'] = parts[2]
                p['password'] = parts[3]

            app.proxies.append(p)

        app.cfg.save_proxies(app.proxies)
        self._update_proxy_display(app.proxies)
        self.add_log(f'🔍 Распарсено {len(app.proxies)} прокси')

    def _update_proxy_display(self, proxies):
        if proxies:
            self.proxy_status.text = f'Загружено: {len(proxies)}'
            lines = []
            for p in proxies[:20]:
                lines.append(f"{p.get('raw', '')} [{p.get('type', 'http')}]")
            if len(proxies) > 20:
                lines.append(f'... и ещё {len(proxies) - 20}')
            self.proxy_list_label.text = '\n'.join(lines)
        else:
            self.proxy_status.text = 'Прокси не загружены'
            self.proxy_list_label.text = ''

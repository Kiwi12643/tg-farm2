# -*- coding: utf-8 -*-
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')
Config.set('kivy', 'log_level', 'info')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

from config import ConfigManager

Window.size = (420, 760)
Window.minimum_width = 360
Window.minimum_height = 640

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.INTERNET,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE
    ])


class LogWidget(MDBoxLayout):
    """Виджет лога внизу экрана"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 200
        self.padding = [8, 4]
        self.spacing = 4

        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=30
        )
        header.add_widget(MDLabel(
            text='📋 ЛОГ',
            theme_text_color='Custom',
            text_color=(0.35, 0.65, 1, 1),
            font_style='Caption',
            bold=True
        ))

        from kivymd.uix.scrollview import MDScrollView
        scroll = MDScrollView()
        self.log_label = MDLabel(
            text='Готов к работе...\n',
            theme_text_color='Custom',
            text_color=(0.8, 0.8, 0.8, 1),
            font_style='Caption',
            size_hint_y=None,
            height=160
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        scroll.add_widget(self.log_label)

        self.add_widget(header)
        self.add_widget(scroll)

    def add_log(self, text):
        current = self.log_label.text
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_label.text = f"[{ts}] {text}\n{current}"
        if len(self.log_label.text) > 3000:
            self.log_label.text = self.log_label.text[:3000]


class NavBar(FakeRectangularElevationBehavior, MDFloatLayout):
    pass


class TGFarmApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cfg = ConfigManager()
        self.accounts = self.cfg.load_accounts()
        self.proxies = self.cfg.load_proxies()
        self.scenarios = self.cfg.load_scenarios()
        self.config_data = self.cfg.load_config()
        self.auth_engine = None
        self.scenario_engine = None
        self.log_widget = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.material_style = "M3"
        self.title = "TG Multi-Tool"

        from screens.auth_screen import AuthScreen
        from screens.proxy_screen import ProxyScreen
        from screens.accounts_screen import AccountsScreen
        from screens.constructor_screen import ConstructorScreen
        from screens.run_screen import RunScreen
        from screens.settings_screen import SettingsScreen

        self.auth_screen = AuthScreen(name='auth')
        self.proxy_screen = ProxyScreen(name='proxy')
        self.accounts_screen = AccountsScreen(name='accounts')
        self.constructor_screen = ConstructorScreen(name='constructor')
        self.run_screen = RunScreen(name='run')
        self.settings_screen = SettingsScreen(name='settings')

        self.sm = MDScreenManager()
        self.sm.add_widget(self.auth_screen)
        self.sm.add_widget(self.proxy_screen)
        self.sm.add_widget(self.accounts_screen)
        self.sm.add_widget(self.constructor_screen)
        self.sm.add_widget(self.run_screen)
        self.sm.add_widget(self.settings_screen)

        root = MDBoxLayout(orientation='vertical')
        self.log_widget = LogWidget()

        self.bottom_nav = MDBottomNavigation(
            panel_color=self.theme_cls.bg_dark,
            text_color_active=(1, 1, 1, 1),
            text_color_normal=(0.5, 0.5, 0.5, 1)
        )

        tab1 = MDBottomNavigationItem(
            name='auth',
            text='АВТОРИЗАЦИЯ',
            icon='account-key'
        )
        tab1.add_widget(self.auth_screen)

        tab2 = MDBottomNavigationItem(
            name='proxy',
            text='ПРОКСИ',
            icon='lan'
        )
        tab2.add_widget(self.proxy_screen)

        tab3 = MDBottomNavigationItem(
            name='accounts',
            text='АККАУНТЫ',
            icon='account-group'
        )
        tab3.add_widget(self.accounts_screen)

        tab4 = MDBottomNavigationItem(
            name='constructor',
            text='СЦЕНАРИИ',
            icon='playlist-plus'
        )
        tab4.add_widget(self.constructor_screen)

        tab5 = MDBottomNavigationItem(
            name='run',
            text='ЗАПУСК',
            icon='play-circle'
        )
        tab5.add_widget(self.run_screen)

        tab6 = MDBottomNavigationItem(
            name='settings',
            text='НАСТРОЙКИ',
            icon='cog'
        )
        tab6.add_widget(self.settings_screen)

        self.bottom_nav.add_widget(tab1)
        self.bottom_nav.add_widget(tab2)
        self.bottom_nav.add_widget(tab3)
        self.bottom_nav.add_widget(tab4)
        self.bottom_nav.add_widget(tab5)
        self.bottom_nav.add_widget(tab6)

        root.add_widget(self.bottom_nav)
        root.add_widget(self.log_widget)

        return root

    def log(self, text):
        if self.log_widget:
            Clock.schedule_once(lambda dt: self.log_widget.add_log(text), 0)
        print(f"[LOG] {text}")

    def on_stop(self):
        if self.auth_engine:
            self.auth_engine.stop()
        if self.scenario_engine:
            self.scenario_engine.stop()
        self.cfg.save_all(self.config_data, self.accounts, self.proxies, self.scenarios)


if __name__ == '__main__':
    TGFarmApp().run()

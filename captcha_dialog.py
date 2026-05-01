# -*- coding: utf-8 -*-
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivy.uix.image import Image
from kivy.metrics import dp
import os


class CaptchaDialogContent(MDBoxLayout):
    def __init__(self, photo_path, question, bot, callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(12)
        self.padding = dp(16)
        self.callback = callback
        self.size_hint_y = None
        self.height = dp(500)

        self.add_widget(MDLabel(
            text=f"🆘 Бот @{bot} просит капчу!",
            theme_text_color='Custom',
            text_color=(1, 0.3, 0.3, 1),
            font_style='H6'
        ))

        self.add_widget(MDLabel(
            text=f"❓ {question}",
            theme_text_color='Custom',
            text_color=(0.9, 0.9, 0.9, 1),
            font_style='Body1'
        ))

        if photo_path and os.path.exists(photo_path):
            img = Image(
                source=photo_path,
                size_hint_y=None,
                height=dp(300)
            )
            self.add_widget(img)

        self.add_widget(MDLabel(
            text="Номера секций через запятую (1-9):",
            theme_text_color='Custom',
            text_color=(0.7, 0.7, 0.7, 1),
            font_style='Caption'
        ))

        self.input_field = MDTextField(
            hint_text="1,3,7",
            mode='rectangle',
            size_hint_y=None,
            height=dp(50)
        )
        self.add_widget(self.input_field)


def show_captcha_dialog(photo_path, question, bot, callback):
    content = CaptchaDialogContent(
        photo_path=photo_path,
        question=question,
        bot=bot,
        callback=callback
    )

    dlg = MDDialog(
        title="",
        type="custom",
        content_cls=content,
        buttons=[
            MDFlatButton(
                text="ПРОПУСТИТЬ",
                on_release=lambda x: (
                    callback([]),
                    dlg.dismiss()
                )
            ),
            MDRaisedButton(
                text="ОТПРАВИТЬ",
                on_release=lambda x: (
                    _parse_and_send(content, callback),
                    dlg.dismiss()
                )
            )
        ]
    )
    dlg.open()


def _parse_and_send(content, callback):
    import re
    text = content.input_field.text
    nums = [int(n) for n in re.findall(r'[1-9]', text)]
    callback(nums)

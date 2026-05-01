# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivymd.app import MDApp

from block_templates import get_all_block_names, get_block_template, search_blocks


class ConstructorScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scenario_steps = []
        self.selected_block_index = -1

        main_layout = MDBoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))

        main_layout.add_widget(MDLabel(
            text='🧩 КОНСТРУКТОР СЦЕНАРИЕВ',
            theme_text_color='Custom',
            text_color=(0.35, 0.65, 1, 1),
            font_style='H5',
            bold=True
        ))

        # Поиск блоков
        self.block_search = MDTextField(
            hint_text='🔍 Поиск блока...',
            mode='rectangle',
            size_hint_y=None,
            height=dp(48)
        )
        self.block_search.bind(text=self._on_search)
        main_layout.add_widget(self.block_search)

        # Две колонки: блоки и сценарий
        split_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(400)
        )

        # Левая колонка — доступные блоки
        left_card = MDCard(
            orientation='vertical',
            padding=dp(8),
            size_hint_x=0.45,
            elevation=3,
            radius=[12]
        )
        left_card.add_widget(MDLabel(
            text='БЛОКИ',
            theme_text_color='Custom',
            text_color=(1, 0.75, 0.3, 1),
            font_style='Caption',
            bold=True,
            size_hint_y=None,
            height=dp(24)
        ))

        self.blocks_scroll = MDScrollView()
        self.blocks_list = MDList(spacing=dp(2))
        self._populate_blocks(get_all_block_names())
        self.blocks_scroll.add_widget(self.blocks_list)
        left_card.add_widget(self.blocks_scroll)

        btn_add = MDRaisedButton(
            text='➕ ДОБАВИТЬ',
            size_hint_y=None,
            height=dp(40),
            md_bg_color=(0.2, 0.5, 0.8, 1)
        )
        btn_add.bind(on_release=self._add_selected_block)
        left_card.add_widget(btn_add)

        split_layout.add_widget(left_card)

        # Правая колонка — сценарий
        right_card = MDCard(
            orientation='vertical',
            padding=dp(8),
            size_hint_x=0.55,
            elevation=3,
            radius=[12]
        )
        right_card.add_widget(MDLabel(
            text='СЦЕНАРИЙ',
            theme_text_color='Custom',
            text_color=(0.35, 0.65, 1, 1),
            font_style='Caption',
            bold=True,
            size_hint_y=None,
            height=dp(24)
        ))

        self.scenario_scroll = MDScrollView()
        self.scenario_list = MDList(spacing=dp(4))
        self.scenario_scroll.add_widget(self.scenario_list)
        right_card.add_widget(self.scenario_scroll)

        btn_row_right = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(4),
            size_hint_y=None,
            height=dp(40)
        )
        btn_up = MDIconButton(icon='arrow-up', on_release=self._move_up)
        btn_down = MDIconButton(icon='arrow-down', on_release=self._move_down)
        btn_del = MDIconButton(icon='delete', on_release=self._delete_selected)
        btn_row_right.add_widget(btn_up)
        btn_row_right.add_widget(btn_down)
        btn_row_right.add_widget(btn_del)
        right_card.add_widget(btn_row_right)

        split_layout.add_widget(right_card)
        main_layout.add_widget(split_layout)

        # Редактор выбранного блока
        self.editor_card = MDCard(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(6),
            size_hint_y=None,
            height=dp(350),
            elevation=4,
            radius=[16]
        )
        self.editor_card.add_widget(MDLabel(
            text='⚙️ РЕДАКТОР БЛОКА',
            theme_text_color='Custom',
            text_color=(1, 0.75, 0.3, 1),
            font_style='Subtitle1',
            bold=True
        ))

        self.editor_scroll = MDScrollView()
        self.editor_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(6),
            padding=dp(4),
            size_hint_y=None
        )
        self.editor_content.bind(
            minimum_height=self.editor_content.setter('height')
        )
        self.editor_scroll.add_widget(self.editor_content)
        self.editor_card.add_widget(self.editor_scroll)

        main_layout.add_widget(self.editor_card)

        # Кнопки сохранения/загрузки
        btn_row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48)
        )
        btn_save = MDRaisedButton(
            text='💾 СОХРАНИТЬ',
            size_hint_x=0.5,
            md_bg_color=(0, 0.55, 0, 1)
        )
        btn_save.bind(on_release=self._save_scenario)
        btn_row.add_widget(btn_save)

        btn_load = MDRaisedButton(
            text='📂 ЗАГРУЗИТЬ',
            size_hint_x=0.5,
            md_bg_color=(0.2, 0.5, 0.8, 1)
        )
        btn_load.bind(on_release=self._load_scenario)
        btn_row.add_widget(btn_load)

        main_layout.add_widget(btn_row)

        self.add_widget(main_layout)

    def _populate_blocks(self, block_names):
        self.blocks_list.clear_widgets()
        for name in block_names:
            item = OneLineListItem(
                text=name,
                on_release=lambda x, n=name: self._select_block(n)
            )
            self.blocks_list.add_widget(item)

    def _on_search(self, instance, text):
        if text:
            filtered = search_blocks(text)
            self._populate_blocks(filtered)
        else:
            self._populate_blocks(get_all_block_names())

    def _select_block(self, name):
        self.selected_block_name = name
        for item in self.blocks_list.children:
            item.bg_color = (0, 0, 0, 0)
        # Находим и подсвечиваем
        for item in self.blocks_list.children:
            if hasattr(item, 'text') and item.text == name:
                item.bg_color = (0.2, 0.4, 0.8, 0.3)

    def _add_selected_block(self, instance):
        if not hasattr(self, 'selected_block_name'):
            self.add_log('⚠️ Выбери блок слева')
            return
        template = get_block_template(self.selected_block_name)
        template['_name'] = self.selected_block_name
        template['_id'] = str(int(__import__('time').time() * 1000))
        self.scenario_steps.append(template)
        self._refresh_scenario_list()

    def _refresh_scenario_list(self):
        self.scenario_list.clear_widgets()
        for i, step in enumerate(self.scenario_steps):
            name = step.get('_name', '?')
            detail = step.get('target', '') or step.get('text', '') or step.get('command', '') or ''
            item = TwoLineListItem(
                text=f"{i+1}. {name}",
                secondary_text=detail[:60],
                on_release=lambda x, idx=i: self._on_step_selected(idx)
            )
            self.scenario_list.add_widget(item)

    def _on_step_selected(self, index):
        self.selected_block_index = index
        self._update_editor(index)

    def _update_editor(self, index):
        self.editor_content.clear_widgets()
        if index < 0 or index >= len(self.scenario_steps):
            return

        step = self.scenario_steps[index]
        self.editor_content.add_widget(MDLabel(
            text=f"Тип: {step.get('_name', '?')}",
            theme_text_color='Custom',
            text_color=(0.35, 0.65, 1, 1),
            font_style='Body2',
            bold=True,
            size_hint_y=None,
            height=dp(30)
        ))

        # Генерируем поля ввода для параметров
        skip_keys = {'_name', '_id', 'type', 'steps', 'options', 'emojis', 'action', 'then', 'else', 'step', 'step_template', 'data'}
        for key, value in step.items():
            if key in skip_keys:
                continue

            label = MDLabel(
                text=f"{key}:",
                theme_text_color='Custom',
                text_color=(0.7, 0.7, 0.7, 1),
                font_style='Caption',
                size_hint_y=None,
                height=dp(20)
            )
            self.editor_content.add_widget(label)

            if isinstance(value, bool):
                from kivymd.uix.selectioncontrol import MDCheckbox
                cb = MDCheckbox(active=value, size_hint_y=None, height=dp(40))
                cb.bind(active=lambda instance, val, k=key: self._update_param(k, val))
                self.editor_content.add_widget(cb)
            elif isinstance(value, (int, float)):
                inp = MDTextField(
                    text=str(value),
                    mode='rectangle',
                    size_hint_y=None,
                    height=dp(40)
                )
                inp.bind(text=lambda instance, val, k=key, t=type(value): self._update_param_typed(k, val, t))
                self.editor_content.add_widget(inp)
            else:
                inp = MDTextField(
                    text=str(value),
                    mode='rectangle',
                    size_hint_y=None,
                    height=dp(40)
                )
                inp.bind(text=lambda instance, val, k=key: self._update_param(k, val))
                self.editor_content.add_widget(inp)

    def _update_param(self, key, value):
        if self.selected_block_index >= 0:
            self.scenario_steps[self.selected_block_index][key] = value

    def _update_param_typed(self, key, value, val_type):
        try:
            if val_type == int:
                value = int(value)
            elif val_type == float:
                value = float(value)
        except:
            pass
        self._update_param(key, value)

    def _move_up(self, instance):
        if self.selected_block_index > 0:
            self.scenario_steps[self.selected_block_index], self.scenario_steps[self.selected_block_index - 1] = \
                self.scenario_steps[self.selected_block_index - 1], self.scenario_steps[self.selected_block_index]
            self.selected_block_index -= 1
            self._refresh_scenario_list()

    def _move_down(self, instance):
        if self.selected_block_index < len(self.scenario_steps) - 1:
            self.scenario_steps[self.selected_block_index], self.scenario_steps[self.selected_block_index + 1] = \
                self.scenario_steps[self.selected_block_index + 1], self.scenario_steps[self.selected_block_index]
            self.selected_block_index += 1
            self._refresh_scenario_list()

    def _delete_selected(self, instance):
        if self.selected_block_index >= 0:
            self.scenario_steps.pop(self.selected_block_index)
            self.selected_block_index = -1
            self._refresh_scenario_list()
            self.editor_content.clear_widgets()

    def _save_scenario(self, instance):
        if not self.scenario_steps:
            self.add_log('⚠️ Сценарий пуст!')
            return
        app = MDApp.get_running_app()
        name = f"Сценарий {len(app.scenarios) + 1}"
        app.scenarios.append({'name': name, 'steps': self.scenario_steps})
        app.cfg.save_scenarios(app.scenarios)
        self.add_log(f'💾 Сценарий "{name}" сохранён ({len(self.scenario_steps)} шагов)')

    def _load_scenario(self, instance):
        app = MDApp.get_running_app()
        if not app.scenarios:
            dlg = MDDialog(
                title='Сценарии',
                text='Нет сохранённых сценариев',
                buttons=[MDFlatButton(text='ОК', on_release=lambda x: dlg.dismiss())]
            )
            dlg.open()
            return

        # Показываем список сценариев в диалоге
        from kivymd.uix.list import MDList
        list_view = MDList()
        for s in app.scenarios:
            item = OneLineListItem(
                text=s['name'],
                on_release=lambda x, sc=s: self._load_scenario_steps(sc)
            )
            list_view.add_widget(item)

        dlg = MDDialog(
            title='Выбери сценарий',
            type='custom',
            content_cls=list_view,
            buttons=[MDFlatButton(text='ОТМЕНА', on_release=lambda x: dlg.dismiss())]
        )
        dlg.open()

    def _load_scenario_steps(self, scenario):
        self.scenario_steps = [dict(s) for s in scenario['steps']]
        self._refresh_scenario_list()
        self.editor_content.clear_widgets()
        self.selected_block_index = -1
        self.add_log(f'📂 Сценарий "{scenario["name"]}" загружен ({len(self.scenario_steps)} шагов)')

    def get_steps(self):
        return [dict(s) for s in self.scenario_steps]

    def add_log(self, text):
        MDApp.get_running_app().log(text)

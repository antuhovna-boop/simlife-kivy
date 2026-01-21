import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

BG_COLOR = get_color_from_hex('#1e1e2e')
BTN_COLOR = get_color_from_hex('#f38ba8')
TEXT_COLOR = get_color_from_hex('#cdd6f4')

Window.clearcolor = BG_COLOR


class GameData:
    def __init__(self, filepath):
        self.filepath = filepath
        self.default_data = {
            "money": 0,
            "subs": 0,
            "click_power": 1,
            "auto_income": 0,
            "upgrades": {"mic": 0, "cam": 0, "pc": 0}
        }
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_data.copy()
        return self.default_data.copy()

    def save_data(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f)


game = None


class StreamerApp(App):
    def build(self):
        global game
        save_path = os.path.join(self.user_data_dir, "streamer_save.json")
        game = GameData(save_path)

        self.root_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        self.stats_layout = GridLayout(cols=2, size_hint_y=0.2)

        self.lbl_money = Label(text=f"Money: ${game.data['money']}", font_size='20sp', color=(0, 1, 0, 1))
        self.lbl_subs = Label(text=f"Income/sec: ${game.data['auto_income']}", font_size='20sp', color=(1, 0, 1, 1))

        self.stats_layout.add_widget(self.lbl_money)
        self.stats_layout.add_widget(self.lbl_subs)
        self.root_layout.add_widget(self.stats_layout)

        self.btn_stream = Button(
            text="GO LIVE!\n(Tap to Stream)",
            font_size='32sp',
            background_color=BTN_COLOR,
            size_hint_y=0.3
        )
        self.btn_stream.bind(on_press=self.on_stream_click)
        self.root_layout.add_widget(self.btn_stream)

        lbl_shop = Label(text="SHOP UPGRADES", size_hint_y=0.1, font_size='24sp', color=TEXT_COLOR)
        self.root_layout.add_widget(lbl_shop)

        self.scroll = ScrollView(size_hint_y=0.4)
        self.shop_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.shop_layout.bind(minimum_height=self.shop_layout.setter('height'))

        self.btn_mic = Button(text=self.get_upgrade_text("mic"), size_hint_y=None, height=150)
        self.btn_mic.bind(on_press=lambda x: self.buy_upgrade("mic"))
        self.shop_layout.add_widget(self.btn_mic)

        self.btn_cam = Button(text=self.get_upgrade_text("cam"), size_hint_y=None, height=150)
        self.btn_cam.bind(on_press=lambda x: self.buy_upgrade("cam"))
        self.shop_layout.add_widget(self.btn_cam)

        self.btn_pc = Button(text=self.get_upgrade_text("pc"), size_hint_y=None, height=150)
        self.btn_pc.bind(on_press=lambda x: self.buy_upgrade("pc"))
        self.shop_layout.add_widget(self.btn_pc)

        self.scroll.add_widget(self.shop_layout)
        self.root_layout.add_widget(self.scroll)

        Clock.schedule_interval(self.auto_income_tick, 1.0)
        return self.root_layout

    def on_stream_click(self, instance):
        income = game.data['click_power']
        game.data['money'] += income
        self.update_labels()
        game.save_data()

    def auto_income_tick(self, dt):
        income = game.data['auto_income']
        if income > 0:
            game.data['money'] += income
            self.update_labels()
            game.save_data()

    def update_labels(self):
        self.lbl_money.text = f"Money: ${game.data['money']}"
        self.lbl_subs.text = f"Income/sec: ${game.data['auto_income']}"
        self.btn_mic.text = self.get_upgrade_text("mic")
        self.btn_cam.text = self.get_upgrade_text("cam")
        self.btn_pc.text = self.get_upgrade_text("pc")

    def get_upgrade_info(self, type_upg):
        lvl = game.data['upgrades'][type_upg]
        if type_upg == "mic":
            cost = 10 * (lvl + 1)
            effect = "Click Power +1"
        elif type_upg == "cam":
            cost = 50 * (lvl + 1)
            effect = "Passive Income +2 $/sec"
        elif type_upg == "pc":
            cost = 200 * (lvl + 1)
            effect = "Passive Income +10 $/sec"
        return cost, effect, lvl

    def get_upgrade_text(self, type_upg):
        cost, effect, lvl = self.get_upgrade_info(type_upg)
        names = {"mic": "Microphone", "cam": "Webcam", "pc": "Gaming PC"}
        return f"{names[type_upg]} (Lvl {lvl})\nCost: ${cost}\nEffect: {effect}"

    def buy_upgrade(self, type_upg):
        cost, effect, lvl = self.get_upgrade_info(type_upg)
        if game.data['money'] >= cost:
            game.data['money'] -= cost
            game.data['upgrades'][type_upg] += 1

            if type_upg == "mic":
                game.data['click_power'] += 1
            elif type_upg == "cam":
                game.data['auto_income'] += 2
            elif type_upg == "pc":
                game.data['auto_income'] += 10

            game.save_data()
            self.update_labels()


if __name__ == '__main__':
    StreamerApp().run()

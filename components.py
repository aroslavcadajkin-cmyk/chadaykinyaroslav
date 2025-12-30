import kivy
kivy.require('2.3.0')

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.color = get_color_from_hex('#FFFFFF')
        
        with self.canvas.before:
            Color(rgba=get_color_from_hex('#4CAF50'))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class AdCard(BoxLayout):
    title = StringProperty("")
    desc = StringProperty("")
    category = StringProperty("")
    type_ = StringProperty("")
    price = StringProperty("")
    location = StringProperty("")
    author = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(150)
        self.padding = dp(10)
        self.spacing = dp(5)
        

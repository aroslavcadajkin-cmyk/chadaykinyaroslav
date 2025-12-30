import kivy
kivy.require('2.3.0')

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

# Импортируем наши модули
from components import RoundedButton, AdCard
from utils import generate_qr_code, validate_email, create_test_user
from models import User, Advertisement

class LoginScreen(Screen):
    def __init__(self, db, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.app = app_instance  # Ссылка на главное приложение
        self.build_ui()
    
    def build_ui(self):
        # ... интерфейс из вашего кода ...
    
    def test_login(self, instance):
        """Тестовый вход"""
        user_id, username = create_test_user(self.db)
        
        # Сохраняем в главном приложении
        self.app.user_id = user_id
        self.app.username = username
        
        # Переходим на главный экран
        self.manager.current = 'main'
        self.manager.get_screen('main').load_ads()

class MainScreen(Screen):
    def __init__(self, db, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.app = app_instance
        self.current_category = "Все"
        self.build_ui()
    
    def build_ui(self):
        # ... интерфейс из вашего кода ...
    
    def load_ads(self):
        """Загрузка объявлений из БД"""
        self.ads_container.clear_widgets()
        
        ads_data = self.db.get_ads(self.current_category)
        
        if not ads_data:
            # Нет объявлений
            label = Label(
                text="Объявлений пока нет\nБудьте первым!",
                font_size=dp(20),
                color=get_color_from_hex('#999999'),
                halign='center',
                size_hint_y=None,
                height=dp(200)
            )
            label.bind(size=label.setter('text_size'))
            self.ads_container.add_widget(label)
            return
        
        # Преобразуем данные в модели и создаем карточки
        for ad_data in ads_data:
            ad = Advertisement.from_db_row(ad_data)
            card = AdCard(
                title=ad.title,
                desc=ad.description[:100] + "..." if len(ad.description) > 100 else ad.description,
                category=ad.category,
                type_=ad.type_,
                price=ad.price,
                location=ad.location,
                author=ad.username or "Аноним"
            )
            self.ads_container.add_widget(card)

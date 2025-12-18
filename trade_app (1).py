import kivy
kivy.require('2.3.0')

import sqlite3
import uuid
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
import os

# Устанавливаем размер окна для удобства
Window.size = (400, 700)

# ==================== БАЗА ДАННЫХ ====================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('trade.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # Пользователи
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qr_code TEXT UNIQUE,
                username TEXT,
                phone TEXT,
                email TEXT,
                reg_date TIMESTAMP
            )
        ''')
        
        # Объявления
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                description TEXT,
                category TEXT,
                type TEXT,
                price TEXT,
                location TEXT,
                date TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        ''')
        
        self.conn.commit()
    
    def register_user(self, qr, name, phone, email):
        try:
            self.cursor.execute('''
                INSERT INTO users (qr_code, username, phone, email, reg_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (qr, name, phone, email, datetime.now()))
            self.conn.commit()
            return self.cursor.lastrowid
        except:
            return None
    
    def get_user_by_qr(self, qr):
        self.cursor.execute('SELECT * FROM users WHERE qr_code = ?', (qr,))
        return self.cursor.fetchone()
    
    def add_ad(self, user_id, title, desc, category, type_, price, location):
        self.cursor.execute('''
            INSERT INTO ads (user_id, title, description, category, type, price, location, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, title, desc, category, type_, price, location, datetime.now()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_ads(self, category="Все"):
        if category == "Все":
            self.cursor.execute('''
                SELECT ads.*, users.username FROM ads 
                JOIN users ON ads.user_id = users.id 
                WHERE ads.active = 1 
                ORDER BY ads.date DESC
            ''')
        else:
            self.cursor.execute('''
                SELECT ads.*, users.username FROM ads 
                JOIN users ON ads.user_id = users.id 
                WHERE ads.active = 1 AND ads.category = ?
                ORDER BY ads.date DESC
            ''', (category,))
        return self.cursor.fetchall()
    
    def get_user_ads(self, user_id):
        self.cursor.execute('SELECT * FROM ads WHERE user_id = ? ORDER BY date DESC', (user_id,))
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

# ==================== КОМПОНЕНТЫ ====================
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
        
        with self.canvas.before:
            Color(rgba=get_color_from_hex('#FFFFFF'))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
            Color(rgba=get_color_from_hex('#E0E0E0'))
            self.border = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Заголовок
        title_layout = BoxLayout(size_hint_y=None, height=dp(30))
        title_label = Label(
            text=self.title,
            font_size=dp(16),
            bold=True,
            color=get_color_from_hex('#000000'),
            halign='left',
            size_hint_x=0.7
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        category_label = Label(
            text=self.category,
            font_size=dp(12),
            color=get_color_from_hex('#666666'),
            halign='right'
        )
        category_label.bind(size=category_label.setter('text_size'))
        
        title_layout.add_widget(title_label)
        title_layout.add_widget(category_label)
        self.add_widget(title_layout)
        
        # Описание
        desc_label = Label(
            text=self.desc,
            font_size=dp(14),
            color=get_color_from_hex('#333333'),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(60)
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        self.add_widget(desc_label)
        
        # Инфо строка
        info_layout = BoxLayout(size_hint_y=None, height=dp(30))
        
        if self.type_ == 'free':
            type_text = "БЕСПЛАТНО"
        else:
            type_text = f"ОБМЕН: {self.price}"
            
        type_label = Label(
            text=type_text,
            font_size=dp(14),
            bold=True,
            color=get_color_from_hex('#4CAF50')
        )
        
        loc_label = Label(
            text=self.location,
            font_size=dp(12),
            color=get_color_from_hex('#666666')
        )
        
        info_layout.add_widget(type_label)
        info_layout.add_widget(loc_label)
        self.add_widget(info_layout)
        
        # Автор
        author_label = Label(
            text=f"Автор: {self.author}",
            font_size=dp(12),
            color=get_color_from_hex('#999999')
        )
        self.add_widget(author_label)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border.pos = [self.pos[0]-1, self.pos[1]-1]
        self.border.size = [self.size[0]+2, self.size[1]+2]

# ==================== ЭКРАНЫ ====================
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        
        # Заголовок
        title = Label(
            text="TRADE APP",
            font_size=dp(32),
            bold=True,
            color=get_color_from_hex('#4CAF50'),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # Подзаголовок
        subtitle = Label(
            text="Обмен и бесплатные вещи",
            font_size=dp(18),
            color=get_color_from_hex('#666666'),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(subtitle)
        
        layout.add_widget(Label(size_hint_y=None, height=dp(50)))
        
        # Кнопка регистрации
        reg_btn = RoundedButton(
            text='РЕГИСТРАЦИЯ ПО QR-КОДУ',
            size_hint_y=None,
            height=dp(50)
        )
        reg_btn.bind(on_release=self.show_registration)
        layout.add_widget(reg_btn)
        
        # Или текст
        or_label = Label(
            text="или используйте тестовый аккаунт:",
            font_size=dp(14),
            color=get_color_from_hex('#999999')
        )
        layout.add_widget(or_label)
        
        # Кнопка тестового входа
        test_btn = Button(
            text='ВОЙТИ КАК ТЕСТОВЫЙ ПОЛЬЗОВАТЕЛЬ',
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex('#2196F3'),
            color=(1, 1, 1, 1)
        )
        test_btn.bind(on_release=self.test_login)
        layout.add_widget(test_btn)
        
        self.add_widget(layout)
    
    def show_registration(self, instance):
        popup = RegistrationPopup()
        popup.open()
    
    def test_login(self, instance):
        # Создаем тестового пользователя если нет
        self.db.cursor.execute("SELECT * FROM users WHERE username='Тестовый'")
        user = self.db.cursor.fetchone()
        
        if not user:
            qr = str(uuid.uuid4())[:8]
            self.db.cursor.execute('''
                INSERT INTO users (qr_code, username, phone, email, reg_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (qr, 'Тестовый', '+79990000000', 'test@test.com', datetime.now()))
            self.db.conn.commit()
            user_id = self.db.cursor.lastrowid
        else:
            user_id = user[0]
        
        # Переходим в главное меню
        app = App.get_running_app()
        app.user_id = user_id
        app.username = 'Тестовый'
        app.root.current = 'main'
        app.root.get_screen('main').load_ads()

class RegistrationPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Регистрация'
        self.size_hint = (0.9, 0.8)
        self.db = Database()
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Поля ввода
        self.name_input = TextInput(
            hint_text='Ваше имя',
            size_hint_y=None,
            height=dp(50),
            multiline=False
        )
        layout.add_widget(self.name_input)
        
        self.phone_input = TextInput(
            hint_text='Телефон',
            size_hint_y=None,
            height=dp(50),
            multiline=False
        )
        layout.add_widget(self.phone_input)
        
        self.email_input = TextInput(
            hint_text='Email',
            size_hint_y=None,
            height=dp(50),
            multiline=False
        )
        layout.add_widget(self.email_input)
        
        layout.add_widget(Label(size_hint_y=None, height=dp(20)))
        
        # Кнопка регистрации
        reg_btn = RoundedButton(
            text='ЗАРЕГИСТРИРОВАТЬСЯ',
            size_hint_y=None,
            height=dp(50)
        )
        reg_btn.bind(on_release=self.register)
        layout.add_widget(reg_btn)
        
        # Кнопка отмены
        cancel_btn = Button(
            text='ОТМЕНА',
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex('#F44336'),
            color=(1, 1, 1, 1)
        )
        cancel_btn.bind(on_release=self.dismiss)
        layout.add_widget(cancel_btn)
        
        self.content = layout
    
    def register(self, instance):
        name = self.name_input.text.strip()
        phone = self.phone_input.text.strip()
        email = self.email_input.text.strip()
        
        if not all([name, phone, email]):
            self.show_message("Заполните все поля!")
            return
        
        # Генерируем QR-код
        qr_code = str(uuid.uuid4())[:8]
        
        # Регистрируем пользователя
        user_id = self.db.register_user(qr_code, name, phone, email)
        
        if user_id:
            self.show_message(f"Успешная регистрация!\nВаш QR-код: {qr_code}", success=True)
            Clock.schedule_once(lambda dt: self.complete_registration(user_id, name), 2)
    
    def complete_registration(self, user_id, name):
        self.dismiss()
        app = App.get_running_app()
        app.user_id = user_id
        app.username = name
        app.root.current = 'main'
        app.root.get_screen('main').load_ads()
    
    def show_message(self, text, success=False):
        popup = Popup(
            title='Информация' if success else 'Ошибка',
            content=Label(text=text),
            size_hint=(0.8, 0.4)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.current_category = "Все"
        
        # Главный контейнер
        main_layout = BoxLayout(orientation='vertical')
        
        # Верхняя панель
        top_bar = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(10), 0, dp(10), 0])
        top_bar.add_widget(Label(text="Товары для обмена", font_size=dp(18), bold=True))
        
        profile_btn = Button(
            text="Профиль",
            size_hint_x=None,
            width=dp(100),
            background_color=get_color_from_hex('#2196F3')
        )
        profile_btn.bind(on_release=self.go_to_profile)
        top_bar.add_widget(profile_btn)
        main_layout.add_widget(top_bar)
        
        # Панель категорий
        categories = ["Все", "Электроника", "Одежда", "Книги", "Мебель", "Другое"]
        self.category_spinner = Spinner(
            text='Все категории',
            values=categories,
            size_hint_y=None,
            height=dp(40),
            background_color=get_color_from_hex('#4CAF50'),
            color=(1, 1, 1, 1)
        )
        self.category_spinner.bind(text=self.on_category_select)
        main_layout.add_widget(self.category_spinner)
        
        # Контейнер для объявлений
        scroll = ScrollView()
        self.ads_container = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.ads_container.bind(minimum_height=self.ads_container.setter('height'))
        scroll.add_widget(self.ads_container)
        main_layout.add_widget(scroll)
        
        # Кнопка добавления
        add_btn = RoundedButton(
            text='+ ДОБАВИТЬ ОБЪЯВЛЕНИЕ',
            size_hint_y=None,
            height=dp(60)
        )
        add_btn.bind(on_release=self.go_to_add_ad)
        main_layout.add_widget(add_btn)
        
        self.add_widget(main_layout)
    
    def on_category_select(self, spinner, text):
        self.current_category = text
        self.load_ads()
    
    def load_ads(self):
        self.ads_container.clear_widgets()
        
        ads = self.db.get_ads(self.current_category)
        
        if not ads:
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
        
        for ad in ads:
            card = AdCard(
                title=ad[2],
                desc=ad[3][:100] + "..." if len(ad[3]) > 100 else ad[3],
                category=ad[4],
                type_=ad[5],
                price=ad[6],
                location=ad[7],
                author=ad[10]
            )
            self.ads_container.add_widget(card)
    
    def go_to_add_ad(self, instance):
        app = App.get_running_app()
        if app.user_id:
            app.root.current = 'add_ad'
        else:
            self.show_message("Сначала войдите в систему")
    
    def go_to_profile(self, instance):
        app = App.get_running_app()
        if app.user_id:
            app.root.current = 'profile'
            app.root.get_screen('profile').load_data()
        else:
            self.show_message("Сначала войдите в систему")
    
    def show_message(self, text):
        popup = Popup(
            title='Информация',
            content=Label(text=text),
            size_hint=(0.8, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
    
    def on_enter(self):
        self.load_ads()

class AddAdScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Заголовок
        title = Label(
            text="Новое объявление",
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(title)
        
        # Поля формы
        self.title_input = TextInput(
            hint_text='Название товара*',
            size_hint_y=None,
            height=dp(50),
            multiline=False
        )
        layout.add_widget(self.title_input)
        
        self.desc_input = TextInput(
            hint_text='Описание*',
            size_hint_y=None,
            height=dp(100),
            multiline=True
        )
        layout.add_widget(self.desc_input)
        
        # Категория
        categories = ["Электроника", "Одежда", "Книги", "Мебель", "Другое"]
        self.category_spinner = Spinner(
            text='Выберите категорию',
            values=categories,
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(self.category_spinner)
        
        # Тип
        types = ["Бесплатно", "Обмен"]
        self.type_spinner = Spinner(
            text='Тип объявления',
            values=types,
            size_hint_y=None,
            height=dp(50)
        )
        self.type_spinner.bind(text=self.on_type_change)
        layout.add_widget(self.type_spinner)
        
        # Поле для обмена (скрыто по умолчанию)
        self.exchange_input = TextInput(
            hint_text='На что хотите обменять?',
            size_hint_y=None,
            height=dp(50),
            multiline=False,
            opacity=0,
            disabled=True
        )
        layout.add_widget(self.exchange_input)
        
        self.location_input = TextInput(
            hint_text='Местоположение*',
            size_hint_y=None,
            height=dp(50),
            multiline=False
        )
        layout.add_widget(self.location_input)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        publish_btn = RoundedButton(text='ОПУБЛИКОВАТЬ')
        publish_btn.bind(on_release=self.publish_ad)
        btn_layout.add_widget(publish_btn)
        
        cancel_btn = Button(
            text='ОТМЕНА',
            background_color=get_color_from_hex('#F44336')
        )
        cancel_btn.bind(on_release=self.go_back)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def on_type_change(self, spinner, text):
        if text == "Обмен":
            self.exchange_input.opacity = 1
            self.exchange_input.disabled = False
        else:
            self.exchange_input.opacity = 0
            self.exchange_input.disabled = True
            self.exchange_input.text = ""
    
    def publish_ad(self, instance):
        app = App.get_running_app()
        
        title = self.title_input.text.strip()
        desc = self.desc_input.text.strip()
        category = self.category_spinner.text
        type_ = self.type_spinner.text.lower()
        price = self.exchange_input.text.strip() if type_ == "обмен" else ""
        location = self.location_input.text.strip()
        
        # Проверка
        if not all([title, desc, location]):
            self.show_message("Заполните обязательные поля!")
            return
        
        if category == "Выберите категорию":
            self.show_message("Выберите категорию!")
            return
        
        if type_ == "обмен" and not price:
            self.show_message("Укажите, на что хотите обменять!")
            return
        
        # Сохраняем в БД
        ad_id = self.db.add_ad(
            app.user_id, title, desc, category, 
            type_, price, location
        )
        
        if ad_id:
            self.show_message("Объявление опубликовано!", success=True)
            self.clear_form()
            Clock.schedule_once(lambda dt: self.go_back(None), 1.5)
    
    def clear_form(self):
        self.title_input.text = ""
        self.desc_input.text = ""
        self.category_spinner.text = "Выберите категорию"
        self.type_spinner.text = "Тип объявления"
        self.exchange_input.text = ""
        self.location_input.text = ""
        self.exchange_input.opacity = 0
        self.exchange_input.disabled = True
    
    def go_back(self, instance):
        app = App.get_running_app()
        app.root.current = 'main'
        app.root.get_screen('main').load_ads()
    
    def show_message(self, text, success=False):
        popup = Popup(
            title='Успех' if success else 'Ошибка',
            content=Label(text=text),
            size_hint=(0.8, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Заголовок
        self.title_label = Label(
            text="Профиль",
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.title_label)
        
        # Информация о пользователе
        self.info_label = Label(
            text="",
            font_size=dp(16),
            halign='left',
            size_hint_y=None,
            height=dp(100)
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        layout.add_widget(self.info_label)
        
        # Мои объявления
        ads_label = Label(
            text="Мои объявления:",
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(ads_label)
        
        # Контейнер для объявлений
        scroll = ScrollView()
        self.my_ads_container = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(5))
        self.my_ads_container.bind(minimum_height=self.my_ads_container.setter('height'))
        scroll.add_widget(self.my_ads_container)
        layout.add_widget(scroll)
        
        # Кнопка назад
        back_btn = Button(
            text='НАЗАД',
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex('#2196F3')
        )
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def load_data(self):
        app = App.get_running_app()
        
        # Загружаем информацию о пользователе
        self.db.cursor.execute("SELECT * FROM users WHERE id = ?", (app.user_id,))
        user = self.db.cursor.fetchone()
        
        if user:
            self.title_label.text = f"Профиль: {user[2]}"
            self.info_label.text = f"""Имя: {user[2]}
Телефон: {user[3]}
Email: {user[4]}
QR-код: {user[1]}
Дата регистрации: {user[5]}"""
        
        # Загружаем объявления пользователя
        self.my_ads_container.clear_widgets()
        ads = self.db.get_user_ads(app.user_id)
        
        if not ads:
            label = Label(
                text="У вас пока нет объявлений",
                color=get_color_from_hex('#999999'),
                size_hint_y=None,
                height=dp(50)
            )
            self.my_ads_container.add_widget(label)
        else:
            for ad in ads:
                ad_layout = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(100),
                    padding=dp(5)
                )
                
                with ad_layout.canvas.before:
                    Color(rgba=get_color_from_hex('#F5F5F5'))
                    RoundedRectangle(pos=ad_layout.pos, size=ad_layout.size, radius=[5])
                
                title_label = Label(
                    text=ad[2],
                    font_size=dp(16),
                    bold=True,
                    color=get_color_from_hex('#000000'),
                    halign='left',
                    size_hint_y=None,
                    height=dp(30)
                )
                title_label.bind(size=title_label.setter('text_size'))
                
                desc_label = Label(
                    text=ad[3][:50] + "..." if len(ad[3]) > 50 else ad[3],
                    font_size=dp(14),
                    color=get_color_from_hex('#666666'),
                    halign='left',
                    size_hint_y=None,
                    height=dp(40)
                )
                desc_label.bind(size=desc_label.setter('text_size'))
                
                info_label = Label(
                    text=f"{ad[4]} • {ad[5]} • {ad[7]}",
                    font_size=dp(12),
                    color=get_color_from_hex('#999999'),
                    size_hint_y=None,
                    height=dp(20)
                )
                
                ad_layout.add_widget(title_label)
                ad_layout.add_widget(desc_label)
                ad_layout.add_widget(info_label)
                self.my_ads_container.add_widget(ad_layout)
    
    def go_back(self, instance):
        app = App.get_running_app()
        app.root.current = 'main'

# ==================== ГЛАВНОЕ ПРИЛОЖЕНИЕ ====================
class TradeApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = None
        self.username = None
    
    def build(self):
        self.title = "Trade App - Обмен вещами"
        
        # Создаем менеджер экранов
        sm = ScreenManager()
        
        # Добавляем экраны
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AddAdScreen(name='add_ad'))
        sm.add_widget(ProfileScreen(name='profile'))
        
        return sm
    
    def on_stop(self):
        # Закрываем БД при выходе
        for screen in self.root.screens:
            if hasattr(screen, 'db'):
                screen.db.close()

# ==================== ЗАПУСК ПРИЛОЖЕНИЯ ====================
if __name__ == '__main__':
    print("=" * 50)
    print("TRADE APP - Приложение для обмена вещами")
    print("=" * 50)
    print("\nИнструкция:")
    print("1. Нажмите 'РЕГИСТРАЦИЯ ПО QR-КОДУ' для создания аккаунта")
    print("2. Или используйте 'ТЕСТОВЫЙ ПОЛЬЗОВАТЕЛЬ' для быстрого старта")
    print("3. В главном меню можно просматривать объявления")
    print("4. Нажмите '+' для добавления своего объявления")
    print("5. В профиле видны ваши объявления и информация\n")
    
    # Создаем папку для данных если нет
    if not os.path.exists('user_data'):
        os.makedirs('user_data')
    
    TradeApp().run()
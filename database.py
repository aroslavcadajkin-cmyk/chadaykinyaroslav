import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('trade.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
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

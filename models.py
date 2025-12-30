class User:
    def __init__(self, id, qr_code, username, phone, email, reg_date):
        self.id = id
        self.qr_code = qr_code
        self.username = username
        self.phone = phone
        self.email = email
        self.reg_date = reg_date
    
    @classmethod
    def from_db_row(cls, row):
        return cls(*row)

class Advertisement:
    def __init__(self, id, user_id, title, description, category, 
                 type_, price, location, date, active=True, username=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.category = category
        self.type_ = type_
        self.price = price
        self.location = location
        self.date = date
        self.active = active
        self.username = username
    
    @classmethod
    def from_db_row(cls, row):
        # row: (id, user_id, title, description, category, type, price, location, date, active, username)
        return cls(
            id=row[0],
            user_id=row[1],
            title=row[2],
            description=row[3],
            category=row[4],
            type_=row[5],
            price=row[6],
            location=row[7],
            date=row[8],
            active=row[9],
            username=row[10] if len(row) > 10 else None
        )

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserPropertyModel(db.Model):
    __tablename__ = 'properties_user_house'

    id_house = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String())
    price = db.Column(db.Float())
    date_last_sold = db.Column(db.String())
    year_сonstruction = db.Column(db.Integer())
    propertytype = db.Column(db.String())
    bedrooms = db.Column(db.Integer())
    lat = db.Column(db.Float())
    lng = db.Column(db.Float())
    user_email = db.Column(db.String())
    
    def __init__(self, title, price, date_last_sold, year_сonstruction, propertytype, bedrooms, lat, lng, user_email):
        self.title = title
        self.price = price
        self.date_last_sold = date_last_sold
        self.year_сonstruction = year_сonstruction
        self.propertytype = propertytype
        self.bedrooms = bedrooms
        self.lat = lat
        self.lng = lng
        self.user_email = user_email

    def __repr__(self):
        return f"{self.title}:{self.price}:{self.date_last_sold}:{self.year_сonstruction}:{self.propertytype}:{self.bedrooms}:{self.lat}:{self.lng}:{self.user_email}"


class UserAccountModel(db.Model):
    __tablename__ = 'user_inform'

    id_user_email = db.Column(db.String(), primary_key=True)
    username = db.Column(db.String())
    phone_number = db.Column(db.Integer())

    def __init__(self, id_user_email, username, phone_number):
        self.id_user_email = id_user_email
        self.username = username
        self.phone_number = phone_number

    def __repr__(self):
        return f"{self.id_user_email}:{self.username}:{self.phone_number}"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__tablename__.columns}


class DataModel(db.Model):
    __tablename__ = 'data_for_prediction'

    id_data = db.Column(db.Integer(), primary_key=True)
    price = db.Column(db.Float())
    dateLastSold = db.Column(db.String())
    yearConstruction = db.Column(db.Integer())
    propertytype = db.Column(db.String())
    bedrooms = db.Column(db.Integer())
    lat = db.Column(db.Float())
    lng = db.Column(db.Float())

    def __init__(self, price, dateLastSold, yearConstruction, propertytype, bedrooms, lat, lng):
        self.price = price
        self.dateLastSold = dateLastSold
        self.yearConstruction = yearConstruction
        self.propertytype = propertytype
        self.bedrooms = bedrooms
        self.lat = lat
        self.lng = lng

    def __repr__(self):
        return f"{self.price}:{self.dateLastSold}:{self.yearConstruction}:{self.propertytype}:{self.bedrooms}:{self.lat}:{self.lng}"


from flask import Flask, request, jsonify
import pandas as pd
from datetime import timedelta, datetime
from pytz import utc
from models import db, UserPropertyModel, UserAccountModel, DataModel
from apscheduler.schedulers.background import BackgroundScheduler
from prediction import prediction
from parser_data import parse


def update_table():
    print('some')
    yesterday = datetime.now() - timedelta(days=1)
    date = yesterday - timedelta(days=299)
    db.engine.execute("DELETE FROM data_for_prediction WHERE \"dateLastSold\" < %s", (str(date),))

    new_day = parse()
    new_day.rename(columns={'date of last sale': 'dateLastSold', 'year of first sale': 'yearConstruction',
                            'propertyType': 'propertytype'}, inplace=True)
    isempty = new_day.empty
    if isempty == False:
        new_day = new_day.iloc[0].values
        price = float(new_day[0])
        dateLastSold = str(new_day[1].date())
        yearConstruction = int(new_day[2])
        propertytype = str(new_day[3])
        bedrooms = int(new_day[4])
        lat = float(new_day[5])
        lng = float(new_day[6])
        new_data = DataModel(price=price, dateLastSold=dateLastSold,
                                       yearConstruction=yearConstruction, propertytype=propertytype,
                                       bedrooms=bedrooms, lat=lat, lng=lng)
        db.session.add(new_data)
        db.session.commit()
    return 'Done'

scheduler = BackgroundScheduler()
scheduler.configure(timezone=utc)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:localhost"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    scheduler.add_job(id='update_table', func=update_table, trigger='cron', hour=1, minute=0, second=0)
    scheduler.start()


FEATURES_COLS = ['bedrooms', 'year', 'lat', 'lng', 'type_Detached', 'type_Flat', 'type_Semi-Detached', 'type_Terraced']
TARGET_COL = 'price'

@app.route('/sing-up', methods = ['POST'])
def singUp():
    email = request.form["email"]
    username = request.form['username']
    phone_number = request.form['phone_number']

    new_properties = UserAccountModel(id_user_email=email, username=username, phone_number=phone_number)
    db.session.add(new_properties)
    db.session.commit()
    return 'Done'


@app.route('/user-properties', methods = ['POST'])
def user_properties():
    date = datetime.today()
    title = request.form['title']
    price = 0
    date_last_sold = date.date()
    year_construction = request.form['year_construction']
    propertytype = request.form['propertyType']
    bedrooms = request.form['bedrooms']
    lat = request.form['lat']
    lng = request.form['lng']
    user_email = request.form['user_email']
    new_properties = UserPropertyModel(title=title, price=price,date_last_sold=date_last_sold,year_сonstruction=year_construction,propertytype=propertytype, bedrooms=bedrooms, lat=lat, lng=lng, user_email=user_email)
    db.session.add(new_properties)
    db.session.commit()
    return 'Done'

@app.route("/account", methods=['POST'])
def account():
    user_email = request.form['user_email']
    user = db.session.query(UserAccountModel).filter_by(id_user_email=str(user_email)).first()
    data = [{
        'name': user.username,
        'phone': user.phone_number,
    }]
    return jsonify(data)


@app.route("/saved-predictions", methods=['POST'])
def saved():
    user_email = request.form['user_email']
    property = db.session.query(UserPropertyModel).filter_by(user_email=str(user_email)).all()

    data = []
    for z in property:
        print(z)
        data.append(
            {
                'title': z.title,
                'price': z.price,
                'date': z.date_last_sold,
                'year': z.year_сonstruction,
                'type': z.propertytype,
                'bedrooms': z.bedrooms,
                'lat': z.lat,
                'lng': z.lng,
            }
        )


    return jsonify(data)

@app.route("/predict", methods=['POST'])
def forecasting():
    dataFrame = pd.read_sql("SELECT * FROM data_for_prediction", db.engine)
    dataFrame.rename(columns={'dateLastSold': 'date of last sale', 'yearConstruction': 'year of first sale',
                            'propertytype': 'propertyType'}, inplace=True)

    price = request.form.get('price')
    date = datetime.today()
    date_last_sale = date.date()
    year = request.form.get('year of first sale')
    propertyType = request.form.get('propertyType')
    bedrooms = request.form.get('bedrooms')
    lat = request.form.get('lat')
    lng = request.form.get('lng')

    users_data = {
        'price': [price],
        'date of last sale': [date_last_sale],
        'year of first sale': [year],
        'propertyType': [propertyType],
        'bedrooms': [bedrooms],
        'lat': [lat],
        'lng': [lng]
    }
    users_data = pd.DataFrame(users_data)


    data = pd.concat([dataFrame[:299], users_data])
    print(len(users_data))
    print(len(dataFrame))
    print(len(data))
    predict, x = prediction(data)

    prices = []
    for price in predict:
        prices.append(str(round(price)))

    dates = []
    for date in x:
        date = pd.to_datetime(date)
        dates.append(str(date.date()))
    data = {
        'prices': prices,
        'dates': dates
    }
    return jsonify(data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555)
import requests
import re
from bs4 import BeautifulSoup
import json
from datetime import timedelta, date, datetime
import pandas as pd


URL = 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490&maxBedrooms=6&minBedrooms=1&propertyTypes=detached%2Cflat%2Csemi-detached%2Cterraced&secondaryDisplayPropertyType=housesandflats&maxDaysSinceAdded=1'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'accept': '*/*'}
HOST = 'https://www.rightmove.co.uk'


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')

    soup = soup.find(text=re.compile('displayAddress'))

    soup = str(soup)
    soup = soup.replace('window.jsonModel = ', '')

    houses = json.loads(soup)

    preparedData = []
    for properties in houses['properties']:
        if properties['bedrooms'] is None:
            properties['bedrooms'] = 0

        date_sold = properties['listingUpdate']['listingUpdateDate']
        if date_sold is not None:
            date_sold = pd.to_datetime(date_sold)
            if date_sold.date() > date(2022, 1, 20):
                first_year = pd.to_datetime(properties['firstVisibleDate'])

                preparedData.append(
                    {
                        'price': properties['price']['amount'],
                        'date of last sale': date_sold.date(),
                        'year of first sale': first_year.year,
                        'propertyType': properties['propertySubType'],
                        'bedrooms': properties['bedrooms'],
                        'lat': properties['location']['latitude'],
                        'lng': properties['location']['longitude']
                    }
                )
    return preparedData


def parse():

    html = get_html(URL)
    if html.status_code == 200:
        houses = []
        html = get_html(URL)
        houses.extend(get_content(html.text))
    else:
        print('Error')

    data = pd.DataFrame(houses)

    data = data.loc[data['propertyType'].str.contains('Detached|Flat|Terraced|Semi-Detached')]
    data['date of last sale'] = pd.to_datetime(data['date of last sale'])
    data.drop_duplicates(subset=['date of last sale'], inplace=True)
    data.sort_values(by='date of last sale', inplace=True, ascending=True)

    yesterday = datetime.now() - timedelta(days=1)
    day = yesterday.day
    month = yesterday.month
    year = yesterday.year

    data = data.loc[data['date of last sale'] == datetime(year, month, day)]
    return data






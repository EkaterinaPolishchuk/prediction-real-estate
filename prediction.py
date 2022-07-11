import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow import keras
from keras.models import *
from keras.layers import *
from sklearn.preprocessing import MinMaxScaler
from datetime import timedelta, datetime


FEATURES_COLS = ['bedrooms', 'year', 'lat', 'lng', 'type_Detached', 'type_Flat', 'type_Semi-Detached', 'type_Terraced']
TARGET_COL = 'price'
TIMESTEPS = 300

scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()


def split_sequences(sequences, n_steps_in, n_steps_out):
    print(len(sequences))
    X, y = list(), list()
    for i in range(len(sequences)):
        end_ix = i + n_steps_in
        out_end_ix = end_ix + n_steps_out - 1
        if out_end_ix > len(sequences):
            break
        seq_x, seq_y = sequences[i:end_ix, :-1], sequences[end_ix - 1:out_end_ix, -1]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)


def data_scaled(data):
    X = pd.DataFrame(columns=FEATURES_COLS, data=scaler_X.transform(data[FEATURES_COLS]))
    target = data[TARGET_COL]
    target = target.values.reshape(-1, 1)
    print(target.shape)
    data = scaler_y.transform(target)
    y = pd.DataFrame(columns=[TARGET_COL], data=data)
    print(y)
    X.insert(0, TARGET_COL, y)
    print(X)
    return X

def mape(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def train_test_split(df):
    split_idx = 389
    print(len(df))
    train = df.iloc[:split_idx, :]
    test = df.iloc[len(df) - split_idx:, :]


    target = train[TARGET_COL]
    target = target.values.reshape(-1, 1)
    print(target.shape)
    print(train[FEATURES_COLS].shape)
    scaler_X.fit(train[FEATURES_COLS])
    scaler_y.fit(target)

    train_scaled = data_scaled(train)
    test_scaled = data_scaled(test)
    return train_scaled, test_scaled


def horizontally_stack_columns(data_scaled, train=True):
    y = data_scaled['price']
    bedrooms = data_scaled['bedrooms']
    year = data_scaled['year']
    lat = data_scaled['lat']
    lng = data_scaled['lng']
    type_Detached = data_scaled['type_Detached']
    type_Flat = data_scaled['type_Flat']
    type_Semi_Detached = data_scaled['type_Semi-Detached']
    type_Terraced = data_scaled['type_Terraced']

    y = y.values.reshape((len(y), 1))
    bedrooms = bedrooms.values.reshape((len(bedrooms), 1))
    year = year.values.reshape((len(year), 1))
    lat = lat.values.reshape((len(lat), 1))
    lng = lng.values.reshape((len(lng), 1))
    type_Detached = type_Detached.values.reshape((len(type_Detached), 1))
    type_Flat = type_Flat.values.reshape((len(type_Flat), 1))
    type_Semi_Detached = type_Semi_Detached.values.reshape((len(type_Semi_Detached), 1))
    type_Terraced = type_Terraced.values.reshape((len(type_Terraced), 1))

    if train == True:
        dataset_train = np.hstack(
            (bedrooms, year, lat, lng, type_Detached, type_Flat, type_Semi_Detached, type_Terraced, y))
        return dataset_train

    elif train == False:
        dataset_test = np.hstack(
            (bedrooms, year, lat, lng, type_Detached, type_Flat, type_Semi_Detached, type_Terraced))
        y_test = y
        return dataset_test, y_test


def lstm():
    opt = keras.optimizers.Adam(clipnorm=1)

    model = Sequential()
    model.add(LSTM(100, activation='relu', return_sequences=True, input_shape=(TIMESTEPS, len(FEATURES_COLS))))
    model.add(LSTM(100, activation='relu'))

    model.add(Dense(90))
    model.add(Activation('linear'))
    model.compile(loss='mse', optimizer=opt)
    return model


def data_preprocessing(df):
    df.rename(columns={'date of last sale': 'date', 'year of first sale': 'year', 'propertyType': 'type'}, inplace=True)

    df = df.astype(
        {'price': np.float64,
         'bedrooms': np.int8,
         'year': np.int8,
         'lat': np.float64,
         'lng': np.float64
         }
    )

    df['date'] = pd.to_datetime(df['date'])
    df = pd.get_dummies(df, columns=['type'])
    df.sort_values(by='date', inplace=True, ascending=True)
    print(len(df))
    df = df.loc[:, ('date', TARGET_COL, *FEATURES_COLS)]

    prices = df.resample(rule='D', on='date').mean()
    prices = prices.interpolate(method='linear')
    print(len(prices))
    mean = prices.mean()
    for z in prices[TARGET_COL]:
        if z > prices[TARGET_COL].mean() + prices[TARGET_COL].std() * 2 or z < prices[TARGET_COL].mean() - prices[TARGET_COL].std() * 2:
            prices[prices[TARGET_COL] == z] = mean

    prices[TARGET_COL] = np.log(prices[TARGET_COL])

    return prices


def prediction(data):
    model = load_model('modelLSTM.h5')
    data = data_preprocessing(data)
    print(len(data))

    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    dataset_test, y = horizontally_stack_columns(data, False)
    target = y
    target = target.reshape(-1, 1)

    scaler_X.fit(dataset_test)
    scaler_y.fit(target)
    dataset_test = scaler_X.fit_transform(dataset_test)
    y = scaler_y.fit_transform(target)

    X = dataset_test.reshape(1, dataset_test.shape[0], dataset_test.shape[1])
    y_pred = model.predict(X)
    y_pred_inv = scaler_y.inverse_transform(y_pred)
    y_pred_inv = np.exp(y_pred_inv)

    now = datetime.now()
    x = []
    next_day = now.date()
    for z in range(90):
        x.append(next_day)
        next_day = next_day + timedelta(days=1)

    return y_pred_inv, x


def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def train_model():
    data = pd.read_csv('file.csv')
    data = data_preprocessing(data)

    train, test = train_test_split(data)
    dataset_train = horizontally_stack_columns(train, True)
    dataset_test, y = horizontally_stack_columns(test, False)

    X_train, y_train = split_sequences(dataset_train, n_steps_in=TIMESTEPS, n_steps_out=90)

    fit_params = {
        'x': X_train,
        'y': y_train,
        'verbose': 1,
        'epochs': 100,
        'batch_size': 16
    }
    model = lstm()
    model.fit(**fit_params)
    model.save('modelLSTM.h5')

# -*- coding: utf-8 -*-
"""timeseries.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1d9IOjHZC4nBWMqZug3S5LdGz7wI6txTr

Nama : Raafi Dimas
Dicoding
"""

#Import library
import numpy as np 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tensorflow as tf
import math
from keras.layers import Dense, LSTM

import warnings
warnings.filterwarnings('ignore')

from google.colab import drive
drive.mount('/content/drive/', force_remount=True)

data = pd.read_csv('/content/drive/MyDrive/Datacolab/london_merged.csv', parse_dates=['timestamp'], index_col='timestamp')
data.head()

data.info()

data.isnull().sum()

data['hour'] = data.index.hour
data['day_of_week'] = data.index.dayofweek
data['day_of_month'] = data.index.day
data['month'] = data.index.month

data

"""# EDA"""

import matplotlib.pyplot

data_by_month = data.resample('M').sum()

time = data_by_month.index.values
test = data_by_month['cnt'].values

plt.figure(figsize=(15,5))
plt.plot(time, test)

"""penjualan diawal tahun 2015 naik pada tahun 2016 tetapi turun pada tahun 2017."""

from sklearn.model_selection import train_test_split
import numpy as np

train_size = int(len(data) * 0.8) # bobot 80%
train, test = data.iloc[0:train_size], data.iloc[train_size:len(data)]

print(train.shape, test.shape)

from sklearn.preprocessing import RobustScaler

transformer = RobustScaler()
cnt_transformer = transformer.fit(train[['cnt']])

train['cnt'] = cnt_transformer.transform(train[['cnt']])

test['cnt'] = cnt_transformer.transform(test[['cnt']])

scale_col = ['t1', 't2', 'hum', 'wind_speed']
scale_transformer = transformer.fit(train[scale_col].to_numpy())

train.loc[:, scale_col] = scale_transformer.transform(
    train[scale_col].to_numpy())

test.loc[:, scale_col] = scale_transformer.transform(
    test[scale_col].to_numpy())

from tqdm import tqdm_notebook as tqdm

#Split the data into x_train and y_train data sets
x_train = []
y_train = []
time_steps = 24
for i in tqdm(range(len(train) - time_steps)):
    x_train.append(train.drop(columns='cnt').iloc[i:i + time_steps].to_numpy())
    y_train.append(train.loc[:,'cnt'].iloc[i + time_steps])

#Convert x_train and y_train to numpy arrays
x_train = np.array(x_train)
y_train = np.array(y_train)

#Create the x_test and y_test data sets
x_test = []
y_test = data.loc[:,'cnt'].iloc[train_size:len(data)]

for i in tqdm(range(len(test) - time_steps)):
    x_test.append(test.drop(columns='cnt').iloc[i:i + time_steps].to_numpy())
    # y_test.append(test.loc[:,'cnt'].iloc[i + time_steps])

#Convert x_test and y_test to numpy arrays
x_test = np.array(x_test)
y_test = np.array(y_test)

print('Train size:')
print(x_train.shape, y_train.shape)
print('Test size:')
print(x_test.shape, y_test.shape)

class my_Callback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if(logs.get('mae') < 0.1):
            print("MAE has reached below 10%")

    def on_train_end(self, epoch, logs={}):
        print('Done')

callbacks = my_Callback()

from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout , LSTM , Bidirectional 
model = Sequential()
model.add(Bidirectional(LSTM(50,input_shape=(x_train.shape[1],x_train.shape[2]))))
model.add(Dropout(0.2))
model.add(Dense(units=1))

optimizer = tf.keras.optimizers.Adam(learning_rate=1.000e-04)
model.compile(loss = tf.keras.losses.Huber(),
                optimizer = optimizer,
                 metrics = ["mae"])

model.summary()

history = model.fit(x_train, y_train, epochs=150, batch_size=24, validation_split=0.2, callbacks = callbacks, shuffle=True)

def show_final_history(history):
    fig, ax = plt.subplots(1, 2, figsize=(15,5))
    ax[0].set_title('Loss')
    ax[0].plot(history.epoch, history.history["loss"], label="Train Loss")
    ax[0].plot(history.epoch, history.history["val_loss"], label="Validation Loss")
    ax[1].set_title('MAE')
    ax[1].plot(history.epoch, history.history["mae"], label="Mae")
    ax[1].plot(history.epoch, history.history["val_mae"], label="Validation Mae")
    ax[0].legend()
    ax[1].legend()

show_final_history(history)
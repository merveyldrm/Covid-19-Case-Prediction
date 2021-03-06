# -*- coding: utf-8 -*-
"""Covid-19 Case Prediction

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13KFS8NDeO6OSsn-CKtqy5TkC9rGYE1Xz
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt 
import matplotlib.colors as mcolors

import random
import math
import operator

confirmed_df = pd.read_csv('time_series_covid19_confirmed_global.csv')
latest_data = pd.read_csv('01-02-2022.csv')

latest_data.head()

latest_data.tail()

tr_confirmed_df = confirmed_df[confirmed_df['Country/Region']=='Turkey']

tr_confirmed_df.head()

col = tr_confirmed_df.keys()

tr_confirmed = tr_confirmed_df.loc[:, col[4]:col[-1]]

dates = tr_confirmed.keys()
tr_cases = []

for i in dates:
    tr_confirmed_sum = tr_confirmed[i].sum()
    tr_cases.append(tr_confirmed_sum)

def daily_increase(data):
    d = [] 
    for i in range(len(data)):
        if i == 0:
            d.append(data[0])
        else:
            d.append(data[i]-data[i-1])
    return d 

def moving_average(data, window_size):
    moving_average = []
    for i in range(len(data)):
        if i + window_size < len(data):
            moving_average.append(np.mean(data[i:i+window_size]))
        else:
            moving_average.append(np.mean(data[i:len(data)]))
    return moving_average

# window size
window = 7

# turkey confirmed cases
tr_daily_increase = daily_increase(tr_cases)
tr_confirmed_avg= moving_average(tr_cases, window)
tr_daily_increase_avg = moving_average(tr_daily_increase, window)

print(tr_daily_increase)
print(tr_daily_increase_avg)

days_since_1_22 = np.array([i for i in range(len(dates))]).reshape(-1, 1)
tr_cases = np.array(tr_cases).reshape(-1,1)

days_in_future = 10
future_forecast = np.array([i for i in range(len(dates)+days_in_future)]).reshape(-1, 1)
adjusted_dates = future_forecast[:-10]

start = '1/22/2020'
start_date = datetime.datetime.strptime(start, '%m/%d/%Y')
future_forecast_dates = []
for i in range(len(future_forecast)):
    future_forecast_dates.append((start_date + datetime.timedelta(days=i)).strftime('%m/%d/%Y'))

# slightly modify the data to fit the model better (regression models cannot pick the pattern)
days_to_skip = 376
X_tr_train, X_tr_test, y_tr_train, y_tr_test = train_test_split(days_since_1_22[days_to_skip:], tr_cases[days_to_skip:], test_size=0.08, shuffle=False)

from sklearn.preprocessing import PolynomialFeatures

# transform tr data for polynomial regression // a version of linear regression

poly_tr = PolynomialFeatures(degree=2)
poly_tr_X_train = poly_tr.fit_transform(X_tr_train)
poly_tr_X_test = poly_tr.fit_transform(X_tr_test)
poly_tr_future_forecast = poly_tr.fit_transform(future_forecast)

from sklearn.linear_model import LinearRegression

# tr polynomial regression
tr_linear_model = LinearRegression(normalize=True, fit_intercept=False)
tr_linear_model.fit(poly_tr_X_train, y_tr_train)
tr_test_linear_pred = tr_linear_model.predict(poly_tr_X_test)
tr_linear_pred = tr_linear_model.predict(poly_tr_future_forecast)

plt.plot(y_tr_test, color='green')
plt.plot(tr_test_linear_pred, color='orange')
plt.legend(['Tr Test Data', 'Polynomial Regression Predictions'])

#turkey cases
adjusted_dates = adjusted_dates.reshape(1, -1)[0]
plt.figure(figsize=(12, 7))
plt.plot(adjusted_dates, tr_cases, color='green')
plt.plot(adjusted_dates, tr_confirmed_avg, linestyle='dashed', color='red')
plt.title('Number of Coronavirus Cases Over Time', size=10)
plt.xlabel('Days Since 1/22/2020 ', size=10)
plt.ylabel('Number of Cases', size=10)
plt.legend(['Turkey Coronavirus Cases', 'Moving Average {} Days'.format(window)], prop={'size': 10})
plt.xticks(size=10)
plt.yticks(size=10)
plt.show()

# turkey daily increase
plt.figure(figsize=(12, 7))
plt.bar(adjusted_dates, tr_daily_increase)
plt.plot(adjusted_dates, tr_daily_increase_avg, color='black', linestyle='dashed')
plt.title('Turkey Daily Increases in Confirmed Cases', size=10)
plt.xlabel('Days Since 1/22/2020', size=10)
plt.ylabel('Number of Cases', size=10)
plt.legend(['Moving Average {} Days'.format(window), 'Turkey Daily Increase in COVID-19 Cases'], prop={'size': 10})
plt.xticks(size=10)
plt.yticks(size=10)
plt.show()

def tr_plot_predictions(x, y, pred, algo_name, color):
    plt.figure(figsize=(10, 7))
    plt.plot(x, y)
    plt.plot(future_forecast, pred, linestyle='dashed', color=color)
    plt.title('Turkey Coronavirus Cases Over Time', size=10)
    plt.xlabel('Days Since 1/22/2020', size=10)
    plt.ylabel('Number of Cases', size=10)
    plt.legend(['Confirmed Cases', algo_name], prop={'size': 10})
    plt.xticks(size=10)
    plt.yticks(size=10)
    plt.show()

tr_plot_predictions(adjusted_dates, tr_cases, tr_linear_pred, 'Polynomial Linear Regression Predictions', 'purple')

tr_plot_predictions(adjusted_dates, tr_cases, tr_linear_pred, 'Polynomial Linear Regression Predictions', 'purple')

# Future predictions using polynomial regression for Turkey
tr_linear_pred = tr_linear_pred.reshape(1,-1)[0]
tr_linear_df = pd.DataFrame({'Date': future_forecast_dates[-10:], 'Polynomial Predicted Number of Total Confirmed Cases Turkey': np.round(tr_linear_pred[-10:])})
tr_linear_df.style.background_gradient(cmap='PuBuGn')
from flask import Flask, request, render_template, redirect, session, url_for, jsonify
from datetime import datetime
import requests
import json
import pandas as pd
import datetime as dttm
import numpy as np
import statistics

app = Flask(__name__)

CHANNEL1_ID = '2341773'
READ_API_KEY1 = 'NT91XJ6T72K52CU8'
CHANNEL2_ID = '2341776'
READ_API_KEY2 = 'A1KF0DNS94YLNVU8'

aqi25Table = [[0,60,0,50],[61,90,50,100],[91,120,100,200],[121,250,200,300]]
aqi10Table = [[0,100,0,50],[101,160,50,100],[161,210,100,200],[211,350,200,300]]

aqiRanges = [[0,50],[51,100],[101,200],[201,300],[301,400],[401,500]]
aqiColors = ["#83ec09","#c1ff12","#fff400", "#d89901", "#ff0000"]
aqiStatements = ["Good","Satisfactory","Moderately Polluted","Poor","Very Poor","Severe"]



def get_aqi(data):
    pm25 = float(data["feeds"][0]['field3'])
    pm10 = float(data["feeds"][0]['field4'])

    for i in aqi25Table:
        if(pm25<=i[1] and pm25>=i[0]):
            BpLow =  i[0]
            BpHigh = i[1]
            ILow = i[2]
            IHigh = i[3]

            aqi25 = ((IHigh-ILow)/(BpHigh-BpLow))*(pm25-BpLow)+ILow
            break

    for i in aqi10Table:
        if(pm10<=i[1] and pm10>=i[0]):
            BpLow =  i[0]
            BpHigh = i[1]
            ILow = i[2]
            IHigh = i[3]

            aqi10 = ((IHigh-ILow)/(BpHigh-BpLow))*(pm10-BpLow)+ILow
            break

    aqi = (aqi25+aqi10)/2
    aqi = int(round(aqi))

    ans = [aqi,]
    for i in range(len(aqiRanges)):
        if(aqi>=aqiRanges[i][0] and aqi<=aqiRanges[i][1]):
            ans.append(aqiColors[i])
            ans.append(aqiStatements[i])
            break
    return ans

def channel_1_data_update():

    url = f'https://api.thingspeak.com/channels/{CHANNEL1_ID}/feeds.csv'
    params = {
        'api_key': READ_API_KEY1,
        'results': 8000
    }
    response = requests.get(url, params=params)
    data=response.text
    print(data)
    with open('channel_1_data.csv', 'w', newline='') as csv_file:
        csv_file.write(data)
    print(f'Data saved to channel_1_data.csv')

def channel_2_data_update():
    url = f'https://api.thingspeak.com/channels/{CHANNEL2_ID}/feeds.csv'
    params = {
        'api_key': READ_API_KEY2,
        'results': 8000
    }
    response = requests.get(url, params=params)
    data=response.text
    with open('channel_2_data.csv', 'w', newline='') as csv_file:
        csv_file.write(data)
    print(f'Data saved to channel_2_data.csv')
            
def process_data(filename):
    fields_to_process = ['field1', 'field2', 'field3', 'field4']
    if(filename == "channel_2_data"):
        indoorSensor = pd.read_csv('channel_2_data.csv')
        indoorSensor['created_at'] = pd.to_datetime(indoorSensor['created_at'])
        indoorSensor.drop(columns=['entry_id'], inplace=True)
        indoorSensor.set_index('created_at', inplace=True)

        Q1 = indoorSensor.quantile(0.25)
        Q3 = indoorSensor.quantile(0.75)

        IQR = Q3 - Q1
        indoorSensor = indoorSensor[~((indoorSensor < (Q1 - 1.5 * IQR)) |(indoorSensor > (Q3 + 1.5 * IQR))).any(axis=1)]

        indoorSensor = indoorSensor.resample('1min').asfreq()
        indoorSensor.interpolate(method='linear', limit=10, inplace=True)
        indoorSensor.dropna(inplace=True)

        indoorSensor = indoorSensor.resample('10min').mean()
        indoorSensor = indoorSensor.dropna()

        indoorSensor['pm25Avg'] = indoorSensor['field3'].rolling(10).mean()
        indoorSensor['pm10Avg'] = indoorSensor['field4'].rolling(10).mean()
        indoorSensor['temperatureAvg'] = indoorSensor['field1'].rolling(10).mean()
        indoorSensor['humidityAvg'] = indoorSensor['field2'].rolling(10).mean()
        indoorSensor = indoorSensor.dropna()


        indoorSensor.to_json('channel_2_data_preprocessed.json')
        indoorSensor.to_csv('channel_2_data_preprocessed.csv')

    
        mean = [indoorSensor[i].mean() for i in fields_to_process]
        median = [indoorSensor[i].median() for i in fields_to_process]
        std = [indoorSensor[i].std() for i in fields_to_process]
        cv = [(indoorSensor[i].std() / indoorSensor[i].mean()) * 100 for i in fields_to_process]

        
        return (mean, median, std, cv)

    elif(filename == "channel_1_data"):
        outdoorSensor = pd.read_csv('channel_1_data.csv')
        outdoorSensor['created_at'] = pd.to_datetime(outdoorSensor['created_at'])
        outdoorSensor.drop(columns=['entry_id'], inplace=True)
        outdoorSensor.set_index('created_at', inplace=True)

        Q1 = outdoorSensor.quantile(0.25)
        Q3 = outdoorSensor.quantile(0.75)

        IQR = Q3 - Q1
        outdoorSensor = outdoorSensor[~((outdoorSensor < (Q1 - 1.5 * IQR)) |(outdoorSensor > (Q3 + 1.5 * IQR))).any(axis=1)]

        outdoorSensor = outdoorSensor.resample('1min').asfreq()
        outdoorSensor.interpolate(method='linear', inplace=True)
        outdoorSensor.dropna(inplace=True)

        outdoorSensor = outdoorSensor.resample('10min').mean()
        outdoorSensor = outdoorSensor.dropna()

        outdoorSensor['pm25Avg'] = outdoorSensor['field3'].rolling(10).mean()
        outdoorSensor['pm10Avg'] = outdoorSensor['field4'].rolling(10).mean()
        outdoorSensor['temperatureAvg'] = outdoorSensor['field1'].rolling(10).mean()
        outdoorSensor['humidityAvg'] = outdoorSensor['field2'].rolling(10).mean()


        outdoorSensor = outdoorSensor.dropna()

        outdoorSensor.to_json('channel_1_data_preprocessed.json')
        outdoorSensor.to_csv('channel_1_data_preprocessed.csv')



    
        mean = [outdoorSensor[i].mean() for i in fields_to_process]
        median = [outdoorSensor[i].median() for i in fields_to_process]
        std = [outdoorSensor[i].std() for i in fields_to_process]
        cv = [(outdoorSensor[i].std() / outdoorSensor[i].mean()) * 100 for i in fields_to_process]
        return (mean, median, std, cv)



def get_notifs():
    return [[]]


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    url = f'https://api.thingspeak.com/channels/{CHANNEL1_ID}/feeds.json'
    params = {'api_key': READ_API_KEY1,'results': 1}
    response = requests.get(url, params=params)
    data1 = json.loads(response.text)

    url = f'https://api.thingspeak.com/channels/{CHANNEL2_ID}/feeds.json'
    params = {'api_key': READ_API_KEY2,'results': 1}
    response = requests.get(url, params=params)
    data2 = json.loads(response.text)

    aqi1 = get_aqi(data1)
    aqi2 = get_aqi(data2)

    notif_list = get_notifs()
    return render_template('index.html', data = data1, data2 = data2, aqi1 = aqi1, aqi2 = aqi2,notifications = notif_list, file = "home.html", open1="open")

@app.route('/statistics', methods=['GET','POST'])
def statistics():
    return redirect("/statistics/Sensor1")

@app.route('/statistics/Sensor1',methods = ['GET','POST'])
def statisticsSensor1():
    notif_list = get_notifs()
    channel_1_data_update()
    stats = process_data("channel_1_data")
    with open('channel_1_data_preprocessed.json') as json_file:
        data1 = json.load(json_file)
        print(data1)
    return render_template('index.html',notifications = notif_list, file = "statistics.html", open2="open", data = data1, stats = stats)

@app.route('/statistics/Sensor2',methods = ['GET','POST'])
def statisticsSensor2():
    notif_list = get_notifs()
    channel_2_data_update()
    stats = process_data("channel_2_data")
    with open('channel_2_data_preprocessed.json') as json_file:
        data1 = json.load(json_file)
        print(data1)
    return render_template('index.html',notifications = notif_list, file = "statistics.html", open2="open", data = data1, stats = stats)

    
@app.route('/circuit', methods=['GET','POST'])
def circuit():
    
    notif_list = get_notifs()
    return render_template('circuit.html', notifications = notif_list, file = "circuit.html", open4="open")


if __name__ == '__main__':
    app.run(debug=True)

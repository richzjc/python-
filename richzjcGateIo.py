#Gate行情功能函数
import json,requests,urllib3;   
import pandas as pd;  
urllib3.disable_warnings()
import time, hashlib, hmac, requests, json
from  btcBase import *
from  MyTT import *
from btcBase import *

biCodes = []
realCodes = []

def setBiCodes(params):
    global biCodes
    biCodes = params


def realLoadCodes():
    if realCodes:
        fenxi()
    else:
        getRealCodes()


def getRealCodes():
    tempCodes = []
    for code in biCodes:
        result = 0
        index = 0
        while result != 200 and index <= 20:
            url = f"https://api.gateio.ws/api/v4/futures/usdt/candlesticks?contract={code.upper()}&limit=2&interval=1d"
            res = requests.get(url)
            lines = []
            if res.status_code == 200:
                lines = json.loads(res.text)
                result = 200
                totalSum = 0.0
                if len(lines) == 1:
                    totalSum = float(lines[0]["sum"])
                elif len(lines) > 1:
                    totalSum = float(lines[0]["sum"]) + float(lines[1]["sum"])
                if totalSum >= 1000000:
                    tempCodes.append(code)
            else:
                index = index + 1
                time.sleep(1)
    global realCodes
    realCodes = tempCodes
    fenxi()
        
def fenxi():
    for code in realCodes:
        result = 0
        index = 0
        while result != 200 and index <= 20:
            url = f"https://api.gateio.ws/api/v4/futures/usdt/candlesticks?contract={code.upper()}&limit=120&interval=1d"
            res = requests.get(url)
            lines = []
            if res.status_code == 200:
                lines = json.loads(res.text)
                result = 200
                if len(lines) > 5:
                    realFenxi(res.text)              
            else:
                index = index + 1
                time.sleep(1)

def realFenxi(text):
    lines =  json.loads(text)
    df=pd.DataFrame(lines,columns=['t','sum','o','c','h','l'])   
    df = df.astype(float)
    df['Date'] = pd.to_datetime(df['t'], unit='s').dt.tz_localize(pytz.utc)
    df['Date'] = df['Date'].dt.tz_convert('Asia/Shanghai')
    df = df.drop('t', axis=1)
    df.set_index('Date', inplace=True)
    makeData(df)
    return df  

def makeData(df):
    """这个是文档描述"""
    #第一步计算closePx的RSI
    df['rsi5'] = RSI(list(map(float, df.c.values)), 5)
    df['rsi10'] = RSI(list(map(float, df.c.values)),10)
    df['rsi20'] = RSI(list(map(float, df.c.values)),20)
    print(df)

def fenxiRsi(rsi5, rsi10, rsi20):
    return False
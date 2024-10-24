#Gate行情功能函数
import json,requests,urllib3;   
import pandas as pd;  
import time, hashlib, hmac, requests, json
from  btcBase import *
from  MyTT import *
from btcBase import *
import math
import mplfinance as mpf

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
                    realFenxi(res.text, code)              
            else:
                index = index + 1
                time.sleep(1)

def realFenxi(text, code):
    lines =  json.loads(text)
    df=pd.DataFrame(lines,columns=['t','sum','o','c','h','l'])   
    df = df.astype(float)
    df['Date'] = pd.to_datetime(df['t'], unit='s').dt.tz_localize(pytz.utc)
    df['Date'] = df['Date'].dt.tz_convert('Asia/Shanghai')
    df = df.drop('t', axis=1)
    df.set_index('Date', inplace=True)
    df = df.rename(columns={'sum': 'Volumn', 'o': 'Open', "h" : "High", "c" : "Close", "l" : "Low"})
    print(df)
    if makeData(df, code):
        print("发送到机器人")


def makeData(df, code):
    """这个是文档描述"""
    #第一步计算closePx的RSI
    df['rsi5'] = RSI(list(map(float, df.Close.values)), 5)
    df['rsi10'] = RSI(list(map(float, df.Close.values)),10)
    df['rsi20'] = RSI(list(map(float, df.Close.values)),20)
    result = fenxiRsi(df)
    if not result:
        return False
    
    diff, dea, macd = MACD(list(map(float, df.Close.values)), 5, 10, 5)
    df['DIFF'] = diff
    df['DEA'] = dea
    df['MACD'] = macd
    result = fenxiMacd(df)
    if not result:
        return False

    K,D,J = KDJ(list(map(float, df.Close.values)), list(map(float, df.High.values)),list(map(float, df.Low.values)),10, 3, 3)
    df["K"] = K
    df["D"] = D
    df["J"] = J

    result = fenxiKDJ(df)
    if not result:
        return False

    df["ma5"] = MA(list(map(float, df.Close.values)), 5)
    df["ma10"] = MA(list(map(float, df.Close.values)), 10)
    df["ma15"] = MA(list(map(float, df.Close.values)), 15)
    df["ma20"] = MA(list(map(float, df.Close.values)), 20)
    df["ma25"] = MA(list(map(float, df.Close.values)), 25)
    df["ma30"] = MA(list(map(float, df.Close.values)), 30)
    df["ma35"] = MA(list(map(float, df.Close.values)), 35)
    df["ma40"] = MA(list(map(float, df.Close.values)), 40)
    df["ma45"] = MA(list(map(float, df.Close.values)), 45)
    df["ma50"] = MA(list(map(float, df.Close.values)), 50)
    df["ma55"] = MA(list(map(float, df.Close.values)), 55)
    df["ma60"] = MA(list(map(float, df.Close.values)), 60)

    result = fenxiMA(df)
    if not result:
        return False

    print(df)
    genPic(df, code, "1d")
    return True

def fenxiMA(df):
    print("分析MA")
    return True

def fenxiKDJ(df):
    lastDf = df.tail(1)
    K = float(lastDf["K"].iloc[0])
    D = float(lastDf["D"].iloc[0])
    J = float(lastDf["J"].iloc[0])
    if math.isnan(K) or math.isnan(D) or math.isnan(J):
        return False
    
    return J > D and J > K

def fenxiMacd(df):
    lastDf = df.tail(1)
    diff = float(lastDf["DIFF"].iloc[0])
    dea = float(lastDf["DEA"].iloc[0])
    if math.isnan(diff) or math.isnan(dea):
        return False

    return diff > dea     

def fenxiRsi(df):
    lastDf = df.tail(1)
    rsi5 = float(lastDf["rsi5"].iloc[0])
    rsi10 = float(lastDf["rsi10"].iloc[0])
    rsi20  = float(lastDf["rsi20"].iloc[0])
    if math.isnan(rsi5) or math.isnan(rsi10):
        return False

    if not math.isnan(rsi20):
        if rsi5 <= rsi10 or rsi5 <= rsi20:
            return False
    else:
        if rsi5 <= rsi10:
            return False
    return True

def genPic(df, code, period):
    title = code + ", " + period
    fig, axe = mpf.plot(df, type='candle', style="yahoo", mav=(5,10,15,20,25,30,35,40,45,50,55,60), volume=False)
    # fig, axe = mpf.plot(df, type='candle', style='yahoo',title=title, volume=True, addplot=lines, returnfig=True)

    buffer = io.BytesIO()
    fig.savefig(buffer, format='jpg')
    plt.close()
    buffer.seek(0)
    md5 = hashlib.md5()
    md5.update(buffer.getvalue())
    md5Value = md5.hexdigest()
    imageBase64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    postImageToBot(imageBase64, md5Value)    

def postImageToBot(imageBase64, md5Value):
        data =  {
            "msgtype": "image",
            "image": {
                "base64": imageBase64,
                "md5":md5Value
            }
        }
        _postToBot(data)

def _postToBot(data):
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=7c5256e0-68cc-4f41-afa5-90ad13c7a87f"
    json_data = json.dumps(data)
    requests.post(url, data=json_data, headers=COMMON_HEADERS)
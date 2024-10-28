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
    tempCodes = biCodes
    # for code in biCodes:
    #     result = 0
    #     index = 0
    #     while result != 200 and index <= 20:
    #         url = f"https://api.gateio.ws/api/v4/futures/usdt/candlesticks?contract={code.upper()}&limit=2&interval=1d"
    #         res = requests.get(url)
    #         lines = []
    #         if res.status_code == 200:
    #             lines = json.loads(res.text)
    #             result = 200
    #             totalSum = 0.0
    #             if len(lines) == 1:
    #                 totalSum = float(lines[0]["sum"])
    #             elif len(lines) > 1:
    #                 totalSum = float(lines[0]["sum"]) + float(lines[1]["sum"])
    #             if totalSum >= 1000000:
    #                 tempCodes.append(code)
    #         else:
    #             index = index + 1
    #             time.sleep(1)
    global realCodes
    realCodes = tempCodes
    fenxi()
        
def fenxi():
    for code in realCodes:
        try:
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
        except Exception as e:
            print("exception\n")
            print(e)

def realFenxi(text, code):
    lines =  json.loads(text)
    df=pd.DataFrame(lines,columns=['t','sum','o','c','h','l'])   
    df = df.astype(float)
    df['Date'] = pd.to_datetime(df['t'], unit='s').dt.tz_localize(pytz.utc)
    df['Date'] = df['Date'].dt.tz_convert('Asia/Shanghai')
    df = df.drop('t', axis=1)
    df.set_index('Date', inplace=True)
    df = df.rename(columns={'sum': 'Volumn', 'o': 'Open', "h" : "High", "c" : "Close", "l" : "Low"})
    makeData(df, code)
    


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

    largeMaList = getLargeMaList(df)
    result = fenxiMA(df, largeMaList)
    if not result:
        return False

    result = fenxiMaNew(df, largeMaList)
    if not result:
        return False
    
    df["ema5"] = EMA(list(map(float, df.Close.values)), 5)
    df["ema10"] = EMA(list(map(float, df.Close.values)), 10)
    df["ema15"] = EMA(list(map(float, df.Close.values)), 15)
    df["ema20"] = EMA(list(map(float, df.Close.values)), 20)
    df["ema25"] = EMA(list(map(float, df.Close.values)), 25)
    df["ema30"] = EMA(list(map(float, df.Close.values)), 30)
    df["ema35"] = EMA(list(map(float, df.Close.values)), 35)
    df["ema40"] = EMA(list(map(float, df.Close.values)), 40)
    df["ema45"] = EMA(list(map(float, df.Close.values)), 45)
    df["ema50"] = EMA(list(map(float, df.Close.values)), 50)
    df["ema55"] = EMA(list(map(float, df.Close.values)), 55)
    df["ema60"] = EMA(list(map(float, df.Close.values)), 60)
    result = fenxiEma(df)
    if not result:
        return False
    print(code)
    print(df)
    genPic(df, code, "1d")
    return True

def fenxiEma(df):
    lastDf = df.tail(3)
    largeMaList = []
    maKey = ["ma5", "ma10", "ma15", "ma20", "ma25", "ma30", "ma35", "ma40", "ma45", "ma50", "ma55", "ma60"]
    closePx0 = float(lastDf["Close"].iloc[-2])
    for key in maKey:
        maValue = float(lastDf[key].iloc[-2])
        if not math.isnan(maValue) and not math.isnan(closePx0) and closePx0 >= maValue:
            largeMaList.append(key)


    if largeMaList:
        for key in largeMaList:
            emaKey = f"ema{key[2:]}"
            emaValue0 = float(lastDf[emaKey].iloc[-2])
            emaValue1 = float(lastDf[emaKey].iloc[-3])
            if not math.isnan(emaValue0) and not math.isnan(emaValue1) and emaValue0 < emaValue1:
                return False
    return True

def getLargeMaList(df):
    lastDf = df.tail(3)
    closePx0 = float(lastDf["Close"].iloc[-2])
    maKey = ["ma5", "ma10", "ma15", "ma20", "ma25", "ma30", "ma35", "ma40", "ma45", "ma50", "ma55", "ma60"]
    largeMaList = []
    for key in maKey:
        maValue = float(lastDf[key].iloc[-2])
        if not math.isnan(maValue) and not math.isnan(closePx0) and closePx0 >= maValue:
            largeMaList.append(key)
    
    if not largeMaList:
        largeMaList.append("ma5")
        largeMaList.append("ma10")
    
    return largeMaList

def fenxiMA(df, largeMaList):
    lastDf = df.tail(3)
    five0 = float(lastDf["ma5"].iloc[-2])
    five1 = float(lastDf["ma5"].iloc[-3])
    if math.isnan(five0) or math.isnan(five1):
        return False

    if five0 <= five1:
        return False
    
    ten0 = float(lastDf["ma10"].iloc[-2])
    if math.isnan(ten0) or ten0 <= 0:
        return False

    closePx0 = float(lastDf["Close"].iloc[-2])
    openPx0 = float(lastDf["Open"].iloc[-2])
    closePx1 = float(lastDf["Close"].iloc[-3])
    openPx1 = float(lastDf["Close"].iloc[-3])
    high1 = float(lastDf["High"].iloc[-3])

    filterFlag0 = openPx1 < closePx1 and closePx0 >= high1 and openPx0 < closePx0 and closePx0 - closePx1 >= closePx1 - openPx1
    filterFlag1 = (closePx0 - closePx1)/closePx1 > (five0 - five1)/five1
    if filterFlag0 and filterFlag1:
        return False
   
    largeCount = 0
    totalCount = 0
    value = 0.0
    newValue = 0.0

    for key in largeMaList:
        maValue0 = float(lastDf[key].iloc[-2])
        maValue1 = float(lastDf[key].iloc[-3])
        if not math.isnan(maValue1):
            value = value + maValue0 - maValue1
            beishu = int(key[2 :])/5
            newValue = newValue + (maValue0 -maValue1) * beishu
            totalCount += 1
            if maValue0 >= maValue1:
                largeCount += 1

    if totalCount - largeCount > 2:
        return False

    if totalCount > 0 and largeCount/totalCount < 0.5:
        return False

    if newValue < 0:
        return False

    if value < 0:
        return False

    return True

def fenxiMaNew(df, largeMaList):
    valueList = []
    


def fenxiKDJ(df):
    lastDf = df.tail(2)
    K = float(lastDf["K"].iloc[-2])
    D = float(lastDf["D"].iloc[-2])
    J = float(lastDf["J"].iloc[-2])
    if math.isnan(K) or math.isnan(D) or math.isnan(J):
        return False
    
    return J > D and J > K

def fenxiMacd(df):
    lastDf = df.tail(2)
    diff = float(lastDf["DIFF"].iloc[-2])
    dea = float(lastDf["DEA"].iloc[-2])
    if math.isnan(diff) or math.isnan(dea):
        return False
    if diff <= 0:
        return False
    return diff > dea     

def fenxiRsi(df):
    lastDf = df.tail(2)
    rsi5 = float(lastDf["rsi5"].iloc[-2])
    rsi10 = float(lastDf["rsi10"].iloc[-2])
    rsi20  = float(lastDf["rsi20"].iloc[-2])
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
    df = df.tail(100)

    hist_pos = df["MACD"].apply(lambda x: x if x >= 0 else 0)
    hist_neg = df["MACD"].apply(lambda x: x if x < 0 else 0)

    panelIndex = 0
    lines = []

    panelIndex += 1
    lines.append(mpf.make_addplot(df['K'], panel=panelIndex, color='purple', label="KDJ", secondary_y=True, width=1))
    lines.append(mpf.make_addplot(df['D'], panel=panelIndex, color='green', secondary_y=True, width=1))
    lines.append(mpf.make_addplot(df['J'], panel=panelIndex, color='red', secondary_y=True, width=1))

    panelIndex += 1
    lines.append(mpf.make_addplot(df['DIFF'], panel=panelIndex, color='purple',label="MACD", secondary_y=True, width=1))
    lines.append(mpf.make_addplot(df['DEA'], panel=panelIndex, color='green',  secondary_y=True, width=1))
    lines.append(mpf.make_addplot(hist_pos, panel=panelIndex, color='red', type="bar",  secondary_y=True, width=1))
    lines.append(mpf.make_addplot(hist_neg, panel=panelIndex, color='green', type="bar",  secondary_y=True, width=1))

    panelIndex += 1
    lines.append(mpf.make_addplot(df['rsi5'], panel=panelIndex, color='purple', label="RSI", secondary_y=True, width=1))
    lines.append(mpf.make_addplot(df['rsi10'],panel=panelIndex, color='green', secondary_y=True, width=1))
    lines.append(mpf.make_addplot(df['rsi20'], panel=panelIndex, color='red', secondary_y=True, width=1))

    panelIndex += 1
    lines.append(mpf.make_addplot(df['ema5'], panel=panelIndex, color='red', secondary_y=True, width=1, label="EMA"))


    mc = mpf.make_marketcolors(up='red', down='green', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc,  base_mpf_style='yahoo') 
    
   
    # 自定义颜色
    figrature = mpf.plot(df, type='candle', style=s, mav=(5,10,15,20,30,45,60), title=title, addplot=lines, volume=False, figscale=1.5)
    
    #  buffer = io.BytesIO()
    # fig.savefig(buffer, format='jpg')
    # plt.close()
    # buffer.seek(0)
    # md5 = hashlib.md5()
    # md5.update(buffer.getvalue())
    # md5Value = md5.hexdigest()
    # imageBase64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    # postImageToBot(imageBase64, md5Value)    

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
#!/usr/bin/env python3

import time,json,requests, os, io, base64,hashlib, requests,json,schedule,pytz
from datetime import timedelta
from  MyTT import *
import mplfinance as mpf
import matplotlib.pyplot as plt ;


COMMON_HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}


def testPlt():
    # 本地调试PLT
    return True

class BtcBase:
    def __init__(self, name, webUrl, enable = True, sleepStart = 2, sleepEnd = 7,bot='1m'):  
        self.name = name.upper()
        self.enable = enable
        self.sleepStart = sleepStart
        self.sleepEnd = sleepEnd
        self.botKey = self.doGetBotKey(bot)
        self.timeout = 10
        self.webUrl = webUrl

    def doGetBotKey(self,bot):
        return '7c5256e0-68cc-4f41-afa5-90ad13c7a87f'

    def getPrice():
        return []
    
    def makeData(self, df):
        df['rsi'] = RSI(list(map(float, df.close.values)), 14)
        df['EMAFAST'] = EMA(list(map(float, df.close.values)),9)
        df['EMALOW'] = EMA(list(map(float, df.close.values)),26)
        df['ema_trend'] = 0
        ema_cross_up = df[(df['EMAFAST'] > df['EMALOW']) & (df['EMAFAST'].shift(1) < df['EMALOW'].shift(1))].index
        df.loc[ema_cross_up, 'ema_trend'] = 1
        ema_cross_down = df[(df['EMAFAST'] < df['EMALOW']) & (df['EMAFAST'].shift(1) > df['EMALOW'].shift(1))].index
        df.loc[ema_cross_down, 'ema_trend'] = -1
        
        df['volume_ratio'] = df['volume'] / df['volume'].shift(1)

        df['14_ema'] = df['close'].ewm(span=14, adjust=False).mean()
        df['26_ema'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['14_ema'] - df['26_ema']
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['hist'] = df['macd'] - df['signal']

        df = df[30:]
        # print(df)
    
    def analysis(self):
        print('分析开始:'+self.name)
        df=self.getPrice()
        rowCount = df.shape[0]
        if rowCount == 0 :
            print('获取数据失败:'+self.name)
            return
        
        self.makeData(df)

        curPrice = float(df.close.values[-1])
        minPrice = df.close.min(); maxPrice = df.close.max()
        minRate = 100*(curPrice - minPrice)/minPrice; maxRate = 100*(maxPrice - curPrice)/maxPrice
        lastRSI = int(df.rsi.values[-1])

        self.sendTextToBot(df, 'RSI')
        self.sendImageToBot(df, 'RSI')
        return
        
        # RSI策略
        if(lastRSI < 35 or lastRSI > 70):
            if ((lastRSI < 30 or lastRSI > 75) and (minRate > 10 or maxRate >10)):
                self.sendImageToBot(df, 'RSI') 
            self.sendTextToBot(df, 'RSI')


        # EMA策略
        curEmaTrend = float(df.ema_trend.values[-1])
        if(curEmaTrend != 0):
            suff = 'ema_up'
            if curEmaTrend < 0:
                suff = 'ema_down'
            self.sendImageToBot(df, suff)
            self.sendTextToBot(df, suff)

        # 成交量
        # curVolumeRatio = float(df.volume_ratio.values[-1])
        # if(curVolumeRatio > 3 and (curPrice * float(df.volume.values[-1]) > 2000)):
        #     self.sendImageToBot(df, "V{:.1g}".format(curVolumeRatio))

        # 下订，目前暂不支持
        self.doMakeOrderWith(df)
        print('分析结束:'+self.name + ", " +str(df.index[-1]))

    def sendTextToBot(self,df,suff):
        cur = float(df.close.values[-1])
        lastRSI = int(df.rsi.values[-1])
        min = df.close.min(); max = df.close.max()
        statis = "[{:.4g}, {:.4g}]".format(min,max)
        rate = "[{:.3g}%, {:.3g}%]".format(100*(cur - min)/min, 100*(max - cur)/max)
        time = (pd.Timestamp(df.index.values[-1:][0]) +timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        message="【{}】{}, {:.3g}, {:.2g}, {}, {}, {}".format(self.name, time, cur, lastRSI, statis, rate, suff)
        self.writeMsg(message)
        colorStr = "warning" if lastRSI > 70 else "info"
        content="<font color=\"{}\">【{}】{:.4g}  {}</font>  {} {} {} {}".format(
            colorStr, self.name, cur, statis, rate, lastRSI, suff, " [查看]({})".format(self.webUrl))
        self.postMarkdownToBot(content)

    def sendImageToBot(self,df, suff):
        cur = float(df.close.values[-1])
        lastRSI = int(df.rsi.values[-1])
        min = df.close.min()
        max = df.close.max()
        
        statis = ",{:.3g}, [{:.3g}, {:.3g}],".format(cur,min,max)
        rate = "[{:.3g}%, {:.3g}%],{:.2g},".format(100*(cur - min)/min, 100*(max - cur)/max,lastRSI)
        title = self.name + statis + rate + suff
        
        lines = [
            mpf.make_addplot(df['EMAFAST'],type='line'),
            mpf.make_addplot(df['EMALOW'],type='line'),
                    
            mpf.make_addplot(df['rsi'], panel=2, color='purple', secondary_y=False, alpha=0.5),
            mpf.make_addplot([35] * len(df), panel=2, color='green', secondary_y=True, alpha=0.5, linestyle='dashed'),
            mpf.make_addplot([70] * len(df), panel=2, color='red', secondary_y=True, alpha=0.5, linestyle='dashed'),


            mpf.make_addplot(df['macd'], panel=3, color='red', secondary_y=False, alpha=0.5),
            mpf.make_addplot(df['signal'], panel=3, color='green', secondary_y=False, alpha=0.5),
            mpf.make_addplot(df['hist'], type='bar', panel=3, color=[('green' if x >= 0 else 'red') for x in df['hist']], secondary_y=False, alpha=0.5),

            
            # mpf.make_addplot(df['WR'], panel=4, color='purple', secondary_y=False, alpha=0.5),
            # mpf.make_addplot([35] * len(df), panel=4, color='green', secondary_y=True, alpha=0.5, linestyle='dashed'),
            # mpf.make_addplot([70] * len(df), panel=4, color='red', secondary_y=True, alpha=0.5, linestyle='dashed'),   
        ]
        
        fig, axe = mpf.plot(df, type='candle', style='yahoo',title=title, volume=True, addplot=lines, returnfig=True)

        index = 0
        for date in df.index:
            if(1 == df.loc[date, 'ema_trend']):
                axe[0].scatter(index, df.loc[date, 'EMAFAST'] * 0.995, color='red', marker='^')
            elif(-1 == df.loc[date,'ema_trend']):
                axe[0].scatter(index, df.loc[date, 'EMALOW'] * 1.005, color='green', marker='v')
            index = index + 1

        if testPlt():
            # print(df)
            mpf.show()
            return
        buffer = io.BytesIO()
        fig.savefig(buffer, format='jpg')
        plt.close()
        buffer.seek(0)

        md5 = hashlib.md5()
        md5.update(buffer.getvalue())
        md5Value = md5.hexdigest()
        imageBase64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        self.postImageToBot(imageBase64, md5Value)
    
    def doMakeOrderWith(self, df):
        pass
        
    def writeMsg(self,message):
        print(message)
        log = open(os.path.join("./log", self.name+".txt"), "a", encoding='utf8')
        log.write(message+"\n")
    
    def isEnablePostBotMessage(self):
        if not self.enable: 
            return False
        # """判断当前时间是否在指定的时间范围内，并执行定时任务"""
        # 外网需要+8
        current_hour = time.localtime().tm_hour
        if current_hour > self.sleepStart and current_hour < self.sleepEnd:
            return False
        return True



    def _postToBot(self,data):
        if not self.isEnablePostBotMessage():
            return
        url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + self.botKey
        json_data = json.dumps(data)
        requests.post(url, data=json_data, headers=COMMON_HEADERS)

    def postTextToBot(self, content):
        data =  {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        self._postToBot(data)
    
    def postMarkdownToBot(self, content):
        data =  {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        self._postToBot(data)
    
    def postImageToBot(self, imageBase64, md5Value):
        data =  {
            "msgtype": "image",
            "image": {
                "base64": imageBase64,
                "md5":md5Value
            }
        }
        self._postToBot(data)

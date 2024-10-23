#Gate行情功能函数
import json,requests,urllib3;   
import pandas as pd;  
urllib3.disable_warnings()
import time, hashlib, hmac, requests, json
from  btcBase import *
from  MyTT import *

host = "https://api.gateio.ws"
key = ''        # api_key
secret = ''     # api_secret

def setKey(realKey):
    global key
    key = realKey

def setSecret(realSecret):
    global secret
    secret = realSecret

class Gateio(BtcBase):
    
    def __init__(self, pair, limit=500, interval='1h'): 
         super(Gateio,self).__init__(pair+"_"+interval,  
                                   "https://www.gate.io/zh/trade/{}".format(pair),
                                   bot=interval,
                                   enable=True)
         self.pair = pair
         self.limit = limit
         self.interval = interval 
         
    def _gen_sign(self, method, url, query_string=None, payload_string=None):
        t = time.time()
        m = hashlib.sha512()
        m.update((payload_string or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
        sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}

    def getPrice(self):  
        url = '/spot/candlesticks'
        prefix = "/api/v4"
        query_param = f'currency_pair={self.pair}&interval={self.interval}&limit={self.limit}'
        sign_headers = self._gen_sign('GET', prefix + url, query_param,"")
        sign_headers.update(COMMON_HEADERS)
        requestUrl = host + prefix + url + "?" + query_param
        print(requestUrl)
        print("分析数据:{}: https://www.gate.io/zh/trade/{}".format(self.name, self.pair))
        res = requests.get(requestUrl, headers=sign_headers, timeout=self.timeout)
        lines = []
        if res.status_code == 200:
            lines =  json.loads(res.text)
        df=pd.DataFrame(lines,columns=['time','amount','close','high','low','open','volume','aa'])
        if len(lines) > 0:
            df = df.drop('aa', axis=1)
            df = df.astype(float)
            df['Date'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize(pytz.utc)
            df['Date'] = df['Date'].dt.tz_convert('Asia/Shanghai')
            df = df.drop('time', axis=1)
            df.set_index('Date', inplace=True)
            print(df)
        return df
    
    @staticmethod
    def job(interval,aggregate):
        for line in open('./watch_gate.txt'):
            if not line.startswith("#"):
                texts=line.split(',')
                # SOL_USDT,240,minute,1m,1
                if len(texts) == 5:
                    pair=texts[0]
                    limit=texts[1]
                    inter=texts[2]
                    inter2=texts[3]
                    aggre=int(texts[4])
                    if interval == inter and aggregate == aggre:
                        item = Gateio(pair, limit=limit, interval=inter2)
                        item.analysis()
                        time.sleep(1)

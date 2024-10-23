# -*- coding:utf-8 -*-
#!/usr/bin/env python3

from gateio import *

def job(interval,aggregate):
    try:
        Gateio.job(interval,aggregate)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    job('minute',1)
    job('minute',5)
    job('minute',15)
    job('hour',1)
    job('hour',4)
    schedule.every().minute.do(job,'minute',1)
    schedule.every(5).minutes.do(job,'minute',5)
    schedule.every(15).minutes.do(job,'minute',15)
    schedule.every().hour.do(job,'hour',1)
    schedule.every(4).hours.do(job,'hour',4)
    while True:
        schedule.run_pending()
        time.sleep(5)
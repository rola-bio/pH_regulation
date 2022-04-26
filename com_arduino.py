# arduinoと通信するだけのファイル
import serial
from serial.tools import list_ports
import pandas as pd
import datetime
import time
from comFunc import SerialData
import os

try:
    os.makedirs("result")
except FileExistsError:
    pass

water1 = SerialData(com = "/dev/cu.usbmodem1101",air=True)
water2 = SerialData(com = "/dev/cu.usbmodem1201")
water3 = SerialData(com = "/dev/cu.usbmodem1301")

waters = [water1,water2,water3]
print("working")

log_interval = 30 # データを平均化するまでの時間

try:
    t0 = time.time()
    day = datetime.datetime.now().day

    while True:
        web_data = dict() # サーバーに送るデータの辞書
        for water in waters:
            result = water.get_data()
            web_data[str(result["box"])] = result # 後で加工しやすいようにbox名をキーにした辞書を追加
        # このあとにデータをwebになげる。printでも良い
        print(web_data)

        t1 = time.time()
        if (t1-t0) > log_interval:  # インターバル時間を過ぎたら
            print("log")
            for water in waters:
                water.organize() # パイル一時データを平均化して、記録用の辞書に保存、
            t0 = time.time() # t0を初期化
        
        if day != datetime.datetime.now().day: # the day change,
            day = datetime.datetime.now().day # update day,
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for water in waters:
                water.water_results =  pd.DataFrame(water.water_results) # 結果をdf化
                if water.air_results:
                    water.air_results =  pd.DataFrame(water.air_results) # 空気関連のデータがあれば、df化して
                    water.air_results.to_csv("result/"+str(time)+"air_result.csv") # csvで保存
            water_df = pd.concat([water1.water_results,water2.water_results,water3.water_results],axis = 0)
            water_df.to_csv("result/"+str(time)+"water_result.csv")
            print("logged")


except KeyboardInterrupt: # プログラムを終了したとき
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for water in waters:
        water.water_results =  pd.DataFrame(water.water_results) # 結果をdf化
        if water.air_results:
            water.air_results =  pd.DataFrame(water.air_results) # 空気関連のデータがあれば、df化して
            water.air_results.to_csv("result/"+str(time)+"air_result.csv") # csvで保存
    water_df = pd.concat([water1.water_results,water2.water_results,water3.water_results],axis = 0)
    water_df.to_csv("result/"+str(time)+"water_result.csv")
    print("logged")
#!/usr/bin/python
from flask import Flask, request, render_template
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi
import json
import serial
from serial.tools import list_ports
import datetime
import time
import random as rd
import pandas as pd
import os
from comFunc import SerialData

# arduinoの通信を開始。port番号は毎回確認したほうが良い
water1 = SerialData(com = "/dev/cu.usbmodem1101",air=True) # 1番だけsensiron付き
water2 = SerialData(com = "/dev/cu.usbmodem1201")
water3 = SerialData(com = "/dev/cu.usbmodem1301")

waters = [water1,water2,water3]

print("working")

log_interval = 30
acid_data = {"box1":0,"box2":0,"box3":0} # acidpumpの稼働時間
alkali_data = {"box1":0,"box2":0,"box3":0} # alkalipumpの稼働時間

try:  # 結果を保存するディレクトリを作っておく
    os.makedirs("result")
except FileExistsError:
    pass


def log_waters(waters):  # watersの結果をただ保存する関数
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for water in waters:
        water.water_results = pd.DataFrame(water.water_results)  # 結果をdf化
        if water.air_results:
            water.air_results = pd.DataFrame(
                water.air_results)  # 空気関連のデータがあれば、df化して
            water.air_results.to_csv(
                "result/"+str(time)+"air_result.csv")  # csvで保存
    water_df = pd.concat(
        [water1.water_results, water2.water_results, water3.water_results], axis=0)
    water_df.to_csv("result/"+str(time)+"water_result.csv")
    print("logged")


# サーバーを立ち上げる
app = Flask(__name__)


@app.route('/')
# 多分これはデコレータ？ファイルかなんかのwdを設定してそう。
# WEBの画面部分であるhtmlのテンプレートを「/」から配信、「/pipe」でWebSocket部分を受け付けます。
def index():
    return render_template('index.html')  # templatesからhtmlファイルを配信
    # render_templateは、templates内のファイルを指定し、そのhtmlファイルをレスポンスで返すメソッドです。


# 後に指定する, localhost:XXXX/~~~~ の~~~~部分を指定。~~~~~を変えればURLが変わる?
@app.route('/test')
def test():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        t0 = time.time()
        day = datetime.datetime.now().day
        cnt = 0
        while True:
            try:
                web_data = dict() # サーバーから送るデータのリスト
                for water in waters:
                    result = water.get_data()
                    web_data[str(result["box"])] = result # 後で加工しやすいようにbox名をキーにした辞書を追加

                # pumpは積算時間をplot
                for key in web_data:
                    web_data[key]["time"] = int(time.time()) # 時間をunixに書き換えちゃう
                    if "PumpAcid" in web_data[key]:
                        acid_data[key] +=  web_data[key]["PumpAcid"]# acidpumpの稼働時間を積算
                        web_data[key]["PumpAcid"] = acid_data[key]
                    if "PumpAlkali" in web_data[key]:
                        alkali_data[key] +=  web_data[key]["PumpAlkali"]# acidpumpの稼働時間を積算
                        web_data[key]["PumpAlkali"] = alkali_data[key]
                ws.send(json.dumps(web_data)) # データをフロントになげる
                print(web_data["box1"],web_data["box2"],web_data["box3"])

                t1 = time.time() # 時間を取得
                if (t1-t0) > log_interval:  # インターバル時間を過ぎたら
                    print("log")
                    for water in waters:
                        water.organize() # パイル一時データを平均化して、記録用の辞書に保存、
                    t0 = time.time() # t0を初期化

                if day != datetime.datetime.now().day: # the day change,
                    day = datetime.datetime.now().day # update day,
                    log_waters(waters)
                
                """
                d = {"box1": {"box": "box1", "pH": rd.uniform(5.5, 6.5), "temp": rd.randint(15, 17),
                              "air-temp": rd.randint(15, 22), "co2": rd.randint(350, 1200), "humidity": rd.randint(20, 90),
                              "time": int(time.time())},
                     "box2": {"box": "box1", "pH": rd.uniform(5.5, 6.5), "temp": rd.randint(10, 12),
                              "time": int(time.time())},
                     "box3": {"box": "box1", "pH": rd.uniform(5.5, 6.5), "temp": rd.randint(17, 22),
                              "time": int(time.time())}}
                d2 = {"box1": {"box": "box1",  "PumpAcid": rd.randint(0, 30),
                               "time": int(time.time())},
                      "box2": {"box": "box1", "PumpAlkali": rd.randint(0, 30),
                               "time": int(time.time())},
                      "box3": {"box": "box1", "PumpAcid": rd.randint(0, 30),
                               "time": int(time.time())}}
                """

            except KeyboardInterrupt:
                print("Something happen..")
                log_waters(waters)
                break
    return


if __name__ == '__main__':
    app.debug = True
    server = pywsgi.WSGIServer(
        ('localhost', 8000), app, handler_class=WebSocketHandler)  # localhost:8000にサーバーを構築
    server.serve_forever()

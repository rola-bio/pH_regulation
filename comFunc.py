# 利用するクラスを格納しているファイル
import serial
from serial.tools import list_ports
import pandas as pd
import datetime
import time

# Serialで受け取った文字列データを辞書に変える


def format_data(data):
    result = dict()
    data_list = data.split(";")
    for single_data in data_list:
        data_name = single_data.split("@")
        name = data_name[-1]
        result["box"] = str(name)

        categories = data_name[0].split(",")
        for category in categories:
            category_value = category.split(":")
            result[str(category_value[0])] = float(category_value[1])
    return result

# 使わないと思うけど、portデータを取得する関数


def search_com_port():
    coms = list_ports.comports()  # ポートデータ取得
    comlist = []
    for com in coms:
        comlist.append(com.device)

    print('Connected COM ports: ' + str(comlist))
    return comlist

# シリアル通信で使うクラス


class SerialData():
    def __init__(self, com, air=False):
        self.temp_results = list() # データの一次保存
        self.ser = serial.Serial(com, 115200)
        self.water_results = list() # 加工後のデータを保存するリスト
        self.air_results = list() # 加工後のデータを保存するリスト
        self.air = air
        print(self.ser.readline())  # 最初のデータをprint
        print(self.ser.readline())  # もう一回print

    # シリアルで値を受け取って、辞書型でデータを返す。
    def get_data(self):
        result = dict() # 結果を格納する変数
        byte_data = self.ser.readline()  # データを文字列に変換
        data = byte_data.decode().strip()  # 文字列をデコードしつつstripでいらない文字列を抜き取る
        data_list = data.split(";") # boxごとにデータが分かれる場合は、　;　で分離
        for single_data in data_list:
            data_name = single_data.split("@") # boxの名前を @ で分離
            name = data_name[-1] # boxの名前は最後に指定して。
            result["box"] = str(name) # 結果のboxを指定

            categories = data_name[0].split(",") #　センサ（取得するデータのカテゴリ）ごとに、[センサ名：value]のブロックを分離
            for category in categories:
                category_value = category.split(":")
                result[str(category_value[0])] = float(category_value[1]) # 前半がセンサ名、後半が取得値
                ### 結果のイメージ {"box":"box1","pH":4.6,"temperature":20}
        self.temp_results.append(result) # 結果を一時的にパイル
        
        if ("PumpAcid" in result) or ("PumpAlkali" in result): # pumpのデータだけのとき, このとき中身はbox,pump稼働時間
            result["time"] = datetime.datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S')  # 結果に時間だけ追加,このときresultのkeyはboxとpumppowerだけ
            self.water_results.append(result) # 最終的な結果に反映

        return result # サーバにデータを送るために、辞書で構造化したデータをreturn

    # パイルしたデータ（辞書のリスト）を処理して、平均値をreturnする。
    def organize(self):
        # パイルしたデータの構造
        # [{"box":"box1","pH":4.6,"temperature":20}, {"box":"box1","pH":5.1,"temperature":22}, {"box":"box1","pH":6.6,"temperature":10}]
        temp_result = pd.DataFrame(self.temp_results) # パイルしたデータをdf化

        water_dict = {
            "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "box": temp_result["box"][0],
            "pH": temp_result["pH"].mean(),
            "temp": temp_result["temp"].mean(),
        }
        self.water_results.append(water_dict) # 最終的な結果に反映

        if self.air: # 空気のデータがあるマイコンのとき
            air_dict = {
                "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "co2": temp_result["co2"].mean(),
                "air-temp": temp_result["air-temp"].mean(),
                "humidity": temp_result["humidity"].mean(),
            }
            self.air_results.append(air_dict) # 最終的な結果に反映

        self.temp_results = list()  # 最後にdatalistを初期化

dependencies for main PC : pyserial, gevent
dependencies for Arduino : Onewire, DallasTemperature, Sparkfun_SCD30_Arduino_Library

pHを5.9~6.1の間で制御します。
15分に一度pHをチェックし、この範囲を超えた場合、最大1分間ポンプを動かすことでpHを制御します。
pH = 3.9 ~ 8.1の間、ポンプは比例制御されています。そのため例えばpH = 5.4の場合15秒間ポンプが回転することになります。


# Name（リポジトリ/プロジェクト/OSSなどの名前）
Arduinoをメインに利用した、pH制御システムです。
各pHセンサに対して、酸剤・アルカリ剤の2種のポンプを想定しています。
またついでに、DS18B20の温度センサとSESIRONのSCD30という温湿度・CO2センサも動かせます。

DFRobotsのpHセンサで取得したデータはArduinoを通じてシリアル通信でメインPCに送られ、
メインPCではPythonの軽量webアプリケーションフレームワーク：Flaskを使って、
ブラウザにデータをリアルタイムで反映します。
# DEMO

![Demo Image 3](/static/img/concept.png)

# Features


# Requirement

Main PC
* Python 3.7.6
* Pandas 1.3.5
* Pyserial 3.5
* gevent 1.4.0
* gevent-websocket 0.10.1
* Flask 1.1.1

Javascript libraries
* d3.v3.min.js
* epoch.min.js
* jquery-3.6.0.min.js

CSS libraries
* epoch.min.css
* normalize.css
* skeleton.css

Arduino (Arduino UNO)
* Onewire.h
* DallasTemperature.h
* Sparkfun_SCD30_Arduino_Library.h

Browser : Google Chrome

Circuits : 
Motor drive (Photo coupler:TLP875, Nch-power MOSFET:2SK4017)
DS18B20 (electrical resistance:4.7kΩ)

Sensor:
pH : Gravity Analog pH Sensor / Meter Pro Kit V2 - DFRobot
Temperature : DS18B20
Temperature(air)・humidity・CO2 : Sensirion SCD30

# Installation

Requirementで列挙したライブラリなどのインストール方法を説明する

```bash
pip install huga_package
```

# Usage
```bash
git clone https://github.com/rola-bio/pH_regulation.git
```
Arduino IDEのライブラリに
* Onewire.h
* DallasTemperature.h
* Sparkfun_SCD30_Arduino_Library.h
を追加。

ArduinoをメインPCに繋いで、それぞれに pH_regulation/arduino/~~.ino のコードを書き込む
port番号を確認して、 com_arduino.pyのport番号を変更。

```bash
cd pH_regulation
python com_arduino.py
```

これでPCからArduinoのセンサ読み取りが可能になる。
同様にport番号を確認して、 app.pyのport番号を変更。

```bash
cd pH_regulation
python app.py
```
を起動して、
```bash
"working"
```
が表示されたら、ブラウザから　localhost:8000にアクセス。
# Note

注意点などがあれば書く

# Author

作成情報を列挙する

* Sakuma Satoru
* 
* a.gunner.sd.eva@icloud.com

# License
ライセンスを明示する

"hoge" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).

社内向けなら社外秘であることを明示してる

"hoge" is Confidential.

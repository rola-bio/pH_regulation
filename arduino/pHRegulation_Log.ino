/*
 # This sample code is used to test the pH meter V1.0.
 # Editor : YouYou
 # Ver    : 1.0
 # Product: analog pH meter
 # SKU    : SEN0161
*/

#include <math.h>
#include <Wire.h>

#define pass (void)0
#define SensorPin A0 // pH meter Analog output to Arduino Analog Input 0
#define Offset 0.23  // deviation compensate
#define LED 13
#define box "box2"
#define samplingInterval 20
#define printInterval 2000  // sampling every 2seconds
#define ArrayLenth 100 // times of collection

// define control status
#define acidMOTOR 5           // HCl motor output to Arduino Digital Output 6
#define alkaliMOTOR 6         // NaOH motor output to Arduino Digital Output 7
#define controlInterval 1800000 //  control every 30minutes = 1,800,000 ms
#define SV 6.0                // SetValue
#define SR 0.2                // SetRange
#define PR 2                // Proportinal Range

#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 13 // データ(黄)で使用するポート番号
#define SENSER_BIT    11      // 精度の設定bit
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

int pHArray[ArrayLenth]; // Store the average value of the sensor feedback
int pHArrayIndex = 0;
void setup(void)
{
    pinMode(LED, OUTPUT);
    pinMode(acidMOTOR, OUTPUT);
    pinMode(alkaliMOTOR, OUTPUT);
    Wire.begin();
    Serial.begin(115200);
    Serial.println("pH meter experiment!"); // Test the serial monitor
    sensors.setResolution(SENSER_BIT);  // set the resolution of DS18B20
}
void loop(void)
{
    static unsigned long samplingTime = millis();
    static unsigned long printTime = millis();
    static unsigned long controlTime = millis();
    static unsigned rotationTime = millis();
    static float power = 0;
    static float pHValue, voltage;
    if (millis() - samplingTime > samplingInterval)
    {
        pHArray[pHArrayIndex++] = analogRead(SensorPin);
        if (pHArrayIndex == ArrayLenth)
            pHArrayIndex = 0;
        voltage = avergearray(pHArray, ArrayLenth) * 5.0 / 1024;
        pHValue = 3.5 * voltage + Offset;
        samplingTime = millis();
    }
    if (millis() - printTime > printInterval) // Every 800 milliseconds, print a numerical, convert the state of the LED indicator
    {
        Serial.print("Voltage:");
        Serial.print(voltage, 2);
        
        Serial.print(",");
        Serial.print("pH: ");
        Serial.print(pHValue, 2);
        
        sensors.requestTemperatures();
        Serial.print(",");
        Serial.print("temp:");
        Serial.print(sensors.getTempCByIndex(0)); //温度の取得&シリアル送信

        Serial.print("@");
        Serial.println(box);
        digitalWrite(LED, digitalRead(LED) ^ 1);
        printTime = millis();
    }

    //ここからpH制御にする
    if (millis() - controlTime > controlInterval)
    {
        power = ((fabs(SV - pHValue) - (SR / 2)) / PR) / 30;
        // pump作動時間を計算,30分のインターバルのうち1分だけ稼働させたいので、30で割る
        if (power > 0.03)
        {
            power = 0.03; //  powerは0.03（3%）未満
        }
        Serial.print("Pump");
        if (pHValue > SV) //  アルカリのとき
        {
            Serial.print("Acid:");
        }else{
            Serial.print("Alkali:");
        }
        Serial.print(power*controlInterval/1000); //稼働時間をprint
        Serial.print("@");
        Serial.println(box);
        controlTime = millis();
    }

    //  ここからポンプ制御
    if (millis() - controlTime > controlInterval * power)
    {                                   //  ポンプ作動時間より長い時間が経ったら
        analogWrite(acidMOTOR, 0);   //  pumpをオフに
        analogWrite(alkaliMOTOR, 0); //  pumpをオフに
    }
    else
    { //  まだ動かす時間なら
        if (pHValue > SV) //  アルカリのとき
        {
            analogWrite(acidMOTOR, 128);  //  acid pumpをオンに
        }
        else
        {
            analogWrite(alkaliMOTOR, 128);  //  alkali pumpをオンに
        }
    }
    
}
double avergearray(int *arr, int number)
{
    int i;
    int max, min;
    double avg;
    long amount = 0;
    if (number <= 0)
    {
        Serial.println("Error number for the array to avraging!/n");
        return 0;
    }
    if (number < 5)
    { // less than 5, calculated directly statistics
        for (i = 0; i < number; i++)
        {
            amount += arr[i];
        }
        avg = amount / number;
        return avg;
    }
    else
    {
        if (arr[0] < arr[1])
        {
            min = arr[0];
            max = arr[1];
        }
        else
        {
            min = arr[1];
            max = arr[0];
        }
        for (i = 2; i < number; i++)
        {
            if (arr[i] < min)
            {
                amount += min; // arr<min
                min = arr[i];
            }
            else
            {
                if (arr[i] > max)
                {
                    amount += max; // arr>max
                    max = arr[i];
                }
                else
                {
                    amount += arr[i]; // min<=arr<=max
                }
            } // if
        }     // for
        avg = (double)amount / (number - 2);
    } // if
    return avg;
}
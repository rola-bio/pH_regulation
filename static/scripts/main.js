let host = "ws://localhost:8000/test";
let ws = new WebSocket(host); // https://developer.mozilla.org/ja/docs/Web/API/WebSocket MDNのWebSocket解説
const boxes = ["box1", "box2", "box3"];
const sensors = ["pH", "temp", "PumpAcid","PumpAlkali"];
const air_parameter = ["air-temp", "humidity", "co2"];
// グラフの描画範囲
const ranges = {
    "temp": [8, 25],
    "pH": [5, 7.5],
    "PumpAcid": [0,1000],
    "PumpAlkali": [0,1000],
    "air-temp": [8, 32],
    "co2": [350, 1200],
    "humidity": [20, 90]
};
// グラフを描画する変数を格納するオブジェクト
const graphs = new Object();

// 水に関係するグラフを設定
for (const box of boxes) {
    for (const sensor of sensors) {
        let epoch_selector = "." + box + "." + sensor + ".epoch";
        console.log(epoch_selector);
        graphs[epoch_selector] = {
            "variable": $(epoch_selector).epoch({ // var lineChartで、グラフを描画
                range: {
                    left: ranges[sensor]
                },
                type: 'time.line',
                data: [{
                    label: "Series 1",
                    values: [],
                    range: ranges[sensor]
                }], //このvaluesに順次値が追加される
                axes: ['left', 'right', 'bottom'],
                ticks: {
                    time: 60
                },
                windowSize: 180 // グラフにプロットできる数
            })
        };
    }
}

// 空気に関係するグラフを設定
for (const air of air_parameter) {
    let epoch_selector = "." + air + ".epoch";
    graphs[epoch_selector] = {
        "variable": $(epoch_selector).epoch({ // var lineChartで、グラフを描画
            range: {
                left: ranges[air]
            },
            type: 'time.line',
            data: [{
                label: "Series 1",
                values: [],
                range: ranges[air]
            }], //このvaluesに順次値が追加される
            axes: ['left', 'right', 'bottom'],
            ticks: {
                time: 10
            },
            windowSize: 120 // グラフにプロットできる数
        })
    };
}

let start = new Date().getTime(); // unix時間を取得
console.log(start);

ws.onmessage = function (message) { // サーバーからメッセージを受信したときに呼び出されるイベントリスナー。
    let message_data = JSON.parse(message.data);
    // 空気関連のデータを送る
    for (const air of air_parameter) {
        if (air in message_data["box1"]) {
            let selector = ".box1." + air + ".value";
            let text = message_data["box1"][air];
            document.querySelector(selector).textContent = text;

            if ((new Date().getTime() - start) > 5000) { // 秒経過したら
                let epoch_selector = "." + air + ".epoch";
                let push_data = {
                    "time": message_data["box1"]["time"],
                    "y": message_data["box1"][air]
                };
                graphs[epoch_selector]["variable"].push([push_data]);
            }
        }
    }
    // 水関連のデータを送る
    for (const box of boxes) {
        for (const sensor of sensors) {
            if (sensor in message_data[box]) {
                let selector = "." + box + "." + sensor + ".value";
                let text = message_data[box][sensor];
                document.querySelector(selector).textContent = text;

                if ((new Date().getTime() - start) > 5000) { // ~~秒経過したら
                    let epoch_selector = "." + box + "." + sensor + ".epoch";
                    let push_data = {
                        "time": message_data[box]["time"],
                        "y": message_data[box][sensor]
                    };
                    graphs[epoch_selector]["variable"].push([push_data]);
                }
            }
        }
    }
    if ((new Date().getTime() - start) > 5000) { // ~~秒経過したら
        console.log(start)
        start = new Date().getTime(); // start時間を更新
    }
};
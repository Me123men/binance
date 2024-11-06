var chartElement = document.getElementById('chart');
if (chartElement) {
    var chart = LightweightCharts.createChart(chartElement, {
        width: 600,
        height: 300,
        layout: {
            background: { type: 'solid', color: '#000000' },
            textColor: 'rgba(255, 255, 255, 0.9)',
        },
        grid: {
            vertLines: { color: 'rgba(197, 203, 206, 0.5)' },
            horzLines: { color: 'rgba(197, 203, 206, 0.5)' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
        },
        timeScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
        },
    });

    var candleSeries = chart.addCandlestickSeries({
        upColor: 'rgba(255, 144, 0, 1)',
        downColor: '#000',
        borderDownColor: 'rgba(255, 144, 0, 1)',
        borderUpColor: 'rgba(255, 144, 0, 1)',
        wickDownColor: 'rgba(255, 144, 0, 1)',
        wickUpColor: 'rgba(255, 144, 0, 1)',
    });

    // Hämta historisk data
    fetch('http://localhost:5000/history')
        .then((r) => {
            if (!r.ok) throw new Error(`HTTP error! Status: ${r.status}`);
            return r.json();
        })
        .then((response) => {
            console.log(response);
            candleSeries.setData(response);
        })
        .catch((error) => {
            console.error("Error fetching data:", error);
        });
} else {
    console.error("Element with id 'chart' not found");
}

// WebSocket för realtidsdata
var binanceSocket = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@kline_15m");  // Ändrat till 15-minuters candlestick

binanceSocket.onmessage = function (event) {
    var message = JSON.parse(event.data);
    var candlestick = message.k;
    
    // Uppdatera nuvarande candlestick med de nödvändiga värdena och konvertera till nummer
    candleSeries.update({
        time: candlestick.t / 1000,  // Omvandlar millisekunder till sekunder
        open: parseFloat(candlestick.o),
        high: parseFloat(candlestick.h),
        low: parseFloat(candlestick.l),
        close: parseFloat(candlestick.c)
    });
};

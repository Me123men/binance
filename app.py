from flask import Flask, render_template, request, flash, redirect, jsonify
from flask_cors import CORS
import config, csv
from binance.client import Client
from binance.enums import *

app = Flask(__name__)
CORS(app)
app.secret_key='bbaaCCCHHHHHYYY553'
client = Client(config.API_KEY, config.API_SECRET)

@app.route("/")
def index():
    account = client.get_account()
    pengar = account['balances']
    exchange_info = client.get_exchange_info() 
    print(exchange_info)
    symbols = exchange_info['symbols']

    return render_template('index.html', minapengar=pengar, symbols=symbols)

@app.route('/buy', methods=['POST'])
def buy():
    print(request.form)
    try:
        order = client.create_order(symbol=request.form['symbol'],
            side= SIDE_BUY,
            type= ORDER_TYPE_MARKET,
            quantity= request.form['quantity'])
    except Exception as e:
        flash(str(e),  "error")

    return redirect('/')

@app.route("/sell2")
def sell():
    return "sell"

@app.route("/settings")
def settings():
    return "settings"

@app.route('/history')
def history():
    candelsticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "1 Jan, 2023", "1 Jan, 2024")
    processed_candlesticks = []
    for data in candelsticks:
        candlestick = {
            "time": data[0]/1000,
            "open": data[1],
            "high": data[2],
            "low": data[3],
            "close": data[4]
        }
        processed_candlesticks.append(candlestick)

    return jsonify(processed_candlesticks)
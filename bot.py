import os
import json
import requests
import threading
from flask import Flask
import websocket
from binance.client import Client

# Flask-server för att göra boten till en webbtjänst
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# Binance-klient och inställningar
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

TELEGRAM_TOKEN = "7571063619:AAGlDIbL4VfN_KntOqGykTHtHYzZFLWUYgo"
TELEGRAM_CHAT_ID = "8069456620"

client = Client(API_KEY, API_SECRET)

# Kryptovalutapar och tidsramar
SYMBOLS = ['shibusdt', 'ethusdt', 'dogeusdt', 'dotusdt', 'duskusdt', 'dogsusdt', 'dydxusdt', 'fttusdt', 'glmrusdt', 'hbarusdt', 'bnbusdt']
TIMEFRAMES = ['5m', '15m', '30m', '1h']
SOCKET = f"wss://stream.binance.com:9443/ws/" + '/'.join([f"{symbol}@kline_{tf}" for symbol in SYMBOLS for tf in TIMEFRAMES])

# Handelsstorlekar per par
TRADE_QUANTITY = {'SHIBUSDT': 100000, 'ETHUSDT': 0.05}

# Data för att spåra stängda ljus
closes = {symbol: [] for symbol in SYMBOLS}

# Funktion för att skicka Telegram-meddelanden
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Telegram-meddelande skickat:", text)
    except Exception as e:
        print("Kunde inte skicka Telegram-meddelande:", e)

# Funktioner för att upptäcka hammarljusformationer
def is_hammer_candle(open_price, close_price, high_price, low_price):
    body = abs(close_price - open_price)
    lower_shadow = open_price - low_price if close_price > open_price else close_price - low_price
    upper_shadow = high_price - close_price if close_price > open_price else high_price - open_price
    return lower_shadow >= (body * 3) and body > upper_shadow

def is_is_hammer_candle(open_price, close_price, high_price, low_price):
    body = abs(close_price - open_price)
    lower_shadow = open_price - low_price if close_price > open_price else close_price - low_price
    upper_shadow = high_price - close_price if close_price > open_price else high_price - open_price
    return upper_shadow >= 2 * body and (lower_shadow == 0 or body > lower_shadow)

def w_is_hammer_candle(open_price, close_price, high_price, low_price):
    body = abs(close_price - open_price)
    lower_shadow = open_price - low_price if close_price > open_price else close_price - low_price
    upper_shadow = high_price - close_price if close_price > open_price else high_price - open_price
    return lower_shadow >= (body * 2) and (upper_shadow == 0 or body > upper_shadow)

# WebSocket-funktioner
def on_open(ws):
    print('Öppnade anslutning')

def on_close(ws):
    print('Stängde anslutning')

def on_message(ws, message):
    global closes

    json_message = json.loads(message)
    candle = json_message['k']
    symbol = json_message['s'].lower()  # Symbolen för att veta vilken valuta som mottagits
    interval = candle['i']  # Tidsram (t.ex. '1m', '5m', etc.)
    is_candle_closed = candle['x']
    close = float(candle['c'])
    open_price = float(candle['o'])
    high = float(candle['h'])
    low = float(candle['l'])

    if is_candle_closed:
        print(f"Ljus stängt för {symbol.upper()} på tidsram {interval} vid {close}")
        closes[symbol].append(close)

        # Kontrollera om hammarljusformation upptäcks för denna tidsram
        if is_hammer_candle(open_price, close, high, low):
            send_telegram_message(f"Hammarljusstake upptäckt på {symbol.upper()} i tidsram {interval} vid pris {close}")
        
        if is_is_hammer_candle(open_price, close, high, low):
            send_telegram_message(f"Hammarljusstake upptäckt på {symbol.upper()} i tidsram {interval} vid pris {close}")

        if w_is_hammer_candle(open_price, close, high, low):
            send_telegram_message(f"Hammarljusstake upptäckt på {symbol.upper()} i tidsram {interval} vid pris {close}")

# Starta WebSocket
def start_websocket():
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    ws.run_forever()

# Starta Flask-server och WebSocket i bakgrunden
if __name__ == "__main__":
    # Starta WebSocket i en separat tråd
    websocket_thread = threading.Thread(target=start_websocket)
    websocket_thread.daemon = True
    websocket_thread.start()

    # Starta Flask-servern
    PORT = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=PORT)



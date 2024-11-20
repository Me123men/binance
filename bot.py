import websocket, json, pprint, numpy, config
import requests
from binance.client import Client
from binance.enums import *

import os

# Hämta från miljövariabler
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

client = Client(config.API_KEY, config.API_SECRET)


# Lista över kryptovalutapar som ska övervakas
SYMBOLS = ['shibusdt', 'ethusdt']
SOCKET = f"wss://stream.binance.com:9443/ws/" + '/'.join([f"{symbol}@kline_1m" for symbol in SYMBOLS])

TRADE_QUANTITY = {'SHIBUSDT': 100000, 'ETHUSDT': 0.05}  # Justera handelsstorleken per symbol

TELEGRAM_TOKEN = "7778387643:AAEOS9wcNTPKKo34vTD3FSkew_MsKWjtcJI"
TELEGRAM_CHAT_ID = "8069456620"

closes = {symbol: [] for symbol in SYMBOLS}

client = Client(config.API_KEY, config.API_SECRET)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Telegram-meddelande skickat:", text)
    except Exception as e:
        print("Kunde inte skicka Telegram-meddelande:", e)

def is_hammer_candle(open_price, close_price, high_price, low_price):
    body = abs(close_price - open_price)
    lower_shadow = open_price - low_price if close_price > open_price else close_price - low_price
    upper_shadow = high_price - close_price if close_price > open_price else high_price - open_price
    
    # Kontrollera om body är minst tre gånger mindre än lower shadow och minst en gång större än upper shadow
    return lower_shadow >= (body * 3) and body > upper_shadow

def on_open(ws):
    print('Öppnade anslutning')

def on_close(ws):
    print('Stängde anslutning')

def on_message(ws, message):
    global closes

    json_message = json.loads(message)
    candle = json_message['k']
    symbol = json_message['s'].lower()  # Symbolen för att veta vilken valuta som mottagits
    is_candle_closed = candle['x']
    close = float(candle['c'])
    open_price = float(candle['o'])
    high = float(candle['h'])
    low = float(candle['l'])

    if is_candle_closed:
        print(f"Ljus stängd för {symbol} vid {close}")
        closes[symbol].append(close)

        # Kontrollera om hammarljusstake
        if is_hammer_candle(open_price, close, high, low):
            send_telegram_message(f"Hammarljusstake upptäckt på {symbol.upper()} vid pris {close}")

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()



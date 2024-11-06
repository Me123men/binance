import websocket, json, pprint, talib, numpy, config
import requests  # För att skicka Telegram-meddelanden
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
RSA_PERIOD = 14
RSA_OVERBOUGHT = 70
RSA_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.05

# Lägg in din riktiga Telegram-token och chat_id här
TELEGRAM_TOKEN = "7778387643:AAEOS9wcNTPKKo34vTD3FSkew_MsKWjtcJI"
TELEGRAM_CHAT_ID = "8069456620"  # Ditt chat_id här

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET)

# Funktion för att skicka Telegram-meddelanden
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Telegram-meddelande skickat:", text)
    except Exception as e:
        print("Kunde inte skicka Telegram-meddelande:", e)

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("Skickar order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
        send_telegram_message(f"Order utförd: {side} {quantity} {symbol}")
        return True
    except Exception as e:
        print("Order misslyckades:", e)
        return False

def on_open(ws):
    print('Öppnade anslutning')

def on_close(ws):
    print('Stängde anslutning')

def on_message(ws, message):
    global closes, in_position

    print('Mottog meddelande')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']
    if is_candle_closed:
        print("Ljus stängd vid {}".format(close))
        closes.append(float(close))
        print("Closes:", closes)

        if len(closes) > RSA_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSA_PERIOD)
            print('Alla RSI beräknade')
            print(rsi)
            last_rsi = rsi[-1]
            print("Den nuvarande RSI är {}".format(last_rsi))

            if last_rsi > RSA_OVERBOUGHT:
                if in_position:
                    print("Sälj, sälj, sälj")
                    order_succeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeded:
                        in_position = False
                else:
                    print("Inget att göra")

            if last_rsi < RSA_OVERSOLD:
                if in_position:
                    print("Inget att göra")
                else:
                    print("KÖP KÖP")
                    order_succeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeded:
                        in_position = True



ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

import config, csv
from binance.client import Client
client = Client(config.API_KEY, config.API_SECRET)
#prices = client.get_all_tickers()
#for price in prices:
 #   print(price)
 
candles = client.get_klines(symbol='BTCUSDT', interval =Client.KLINE_INTERVAL_1DAY)
csvfile = open('hela.csv', 'w', newline='')
candlestick_writer = csv.writer(csvfile, delimiter=',')

#for candlestick in candles:
 #   print(candlestick)
  #  candlestick_writer.writerow(candlestick)
   # print(len(candles))
candelsticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "1 Jan, 2023", "1 Jan, 2024")
for candelstick in candelsticks:
    candlestick_writer.writerow(candelstick)
csvfile.close()


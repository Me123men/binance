import json

# Funktion för att avgöra om det är en doji-candlestick


def is_doji(candle):
    return abs(float(candle['o']) - float(candle['c'])) < 0.01 * (float(candle['h']) - float(candle['l']))

# Funktion för att avgöra om det är en hammer-candlestick


def is_hammer(candle):
    body = abs(float(candle['o']) - float(candle['c']))
    upper_shadow = float(candle['h']) - \
        max(float(candle['o']), float(candle['c']))
    lower_shadow = min(float(candle['o']), float(
        candle['c'])) - float(candle['l'])
    return body > upper_shadow and body < lower_shadow * 0.75


# Öppna filen för läsning
with open('utmatningsfil.txt', 'r') as file:
    # Loopa igenom varje rad i filen
    for line in file:
        # Läs kline-data från varje rad och konvertera till dictionary
        kline_data = json.loads(line.strip())

        # Kolla om det är en doji-candlestick
        if is_doji(kline_data['k']):
            print("Doji candlestick hittad:", kline_data)

        # Kolla om det är en hammer-candlestick
        if is_hammer(kline_data['k']):
            print("Hammer candlestick hittad:", kline_data)

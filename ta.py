import numpy
import talib
from numpy import genfromtxt

my_data = genfromtxt('1day.csv', delimiter=',')
print(my_data)

close = my_data[:, 4]
print(close)

#close = numpy.random.random(100)
#print(close)

#moving_average = talib.SMA(close)
#print(moving_average)

rsa = talib.RSI(close)
print(rsa)
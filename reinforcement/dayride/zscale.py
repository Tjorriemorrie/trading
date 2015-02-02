import pandas as pd
from sklearn.preprocessing import scale

data = [1, 2, 2, 5]
ser = pd.Series(data, dtype=float)
print ser
print ser.describe()

print 'scaled 1'
scale(ser, copy=False)
print ser
print ser.describe()

print 'scaled 2'
scale(ser, copy=False)
print ser
print ser.describe()

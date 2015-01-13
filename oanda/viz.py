import json
from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt


with open('data/EURUSD3600.json') as f:
    data = json.loads(f.read())

data = OrderedDict(sorted(data.items()))

for i, v in data.iteritems():
    print 'timestamp', i
    print v['rate']
    points = OrderedDict(sorted(v['price_points'].items()))
    for k, d in points.iteritems():
        print k
    print points
    plt.scatter(i, v['rate'])

plt.show()


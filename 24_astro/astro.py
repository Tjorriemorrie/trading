import flatlib
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos


def generate_data():
    date = Datetime('2015/01/13', '17:00', '+10:00')
    print(date)

    pos = GeoPos('38n32', '8w54')
    print(pos)

    chart = Chart(date, pos)
    print(chart)


if __name__ == '__main__':
    generate_data()

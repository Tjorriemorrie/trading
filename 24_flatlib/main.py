import datetime
from typing import NoReturn

from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos


def get_chart() -> Chart:
    date = Datetime('2015/03/13', '17:00', '+00:00')
    pos = GeoPos('38n32', '8w54')
    chart = Chart(date, pos)
    print(chart)
    return chart


def main() -> NoReturn:
    chart = get_chart()
    print('ok')


if __name__ == '__main__':
    main()

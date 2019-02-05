from datetime import datetime, timedelta
from typing import NoReturn

import pandas as pd
from flatlib.chart import Chart
from flatlib.const import LIST_SIGNS
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

ASTRO_FILE = 'astro.csv'


def get_chart(date: datetime) -> Chart:
    date = Datetime(date.strftime('%Y/%m/%d'))
    pos = GeoPos('38n32', '8w54')
    chart = Chart(date, pos)
    # print(chart)
    return chart


def main() -> NoReturn:
    date = datetime(2003, 1, 21)
    end_date = datetime(2019, 1, 31)
    one_day = timedelta(days=1)
    print(f'generating data from {date} to {end_date} every {one_day}')

    labels, uniques = pd.factorize(LIST_SIGNS)
    signs_map = {s: l for s, l in zip(LIST_SIGNS, labels)}
    print(f'signs map created: {signs_map}')

    data = []
    while date < end_date:
        chart = get_chart(date)
        row = {'date': str(date)}
        for object in chart.objects:
            for p in vars(object):
                if p in ['id', 'type']:
                    continue
                attr = getattr(object, p)
                if p == 'sign':
                    attr = signs_map[attr]
                row[f'{object.id}_{p}'] = attr
        data.append(row)
        # for house in chart.houses:
        #     pass
        # for angle in chart.angles:
        #     pass
        date += one_day

    df = pd.DataFrame(data)
    print('dataframe created')

    df['date'] = pd.to_datetime(df['date']).dt.date
    df.set_index('date', inplace=True)
    print('datetime index set')

    df.to_csv(ASTRO_FILE)
    print('done')


if __name__ == '__main__':
    main()

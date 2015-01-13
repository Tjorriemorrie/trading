import pandas as pd


def main():
    # get data
    df = pd.io.parsers.read_csv(
        filepath_or_buffer='data/EURUSD1440.csv',
        header=None,
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        parse_dates=[[0, 1]],
    )
    # print df

    df['diff'] = df['close'].diff(periods=1)
    # print df

    df['target'] = pd.rolling_sum(df['diff'], 2).shift(-2)
    # print df

    for col in ['open', 'high', 'low', 'close']:
        cmin = df[col].min()
        cmax = df[col].max()
        df[col] = df[col].apply(lambda x: round((x - cmin) / (cmax - cmin), 1))
    print df[100:200]

    df.to_csv('transformed.csv')


if __name__ == '__main__':
    main()
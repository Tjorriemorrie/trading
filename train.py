import pandas as pd


def main():
    df = pd.io.parsers.read_csv(
        filepath_or_buffer='transformed.csv',
        # header=None,
        # names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'],
        # parse_dates=[[0, 1]],
        index_col=0,
    )
    print df


if __name__ == '__main__':
    main()
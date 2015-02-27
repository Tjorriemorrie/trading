import logging
import argparse
from brain.network import Network
from brain.nucleus import Nucleus


def main(debug):
    logging.info('Starting...')
    network = Network(28*28)
    logging.info('The End')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    debug = args.debug
    lvl = logging.DEBUG if debug else logging.WARN

    logging.basicConfig(
        level=lvl,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    main(debug)
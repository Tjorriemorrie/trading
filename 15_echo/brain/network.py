import logging
from nucleus import Nucleus


class Network:

    inputs = []
    nucli = []


    def __init__(self, n=10):
        logging.info('Network: init')

        if not self.inputs:
            for m in xrange(n):
                self.nucli.append(Nucleus())
                self.inputs.append(Nucleus())
            logging.info('Initiated with {0} input neurons'.format(n))


    def addNucli(self, n):
        logging.info('Add {0} nucli'.format(n))

        logging.info('{0} nucli added {1} total'.format(n, len(self.nucli)))

        for m in self.nucli[-n:]:
            logging.info('{0}'.format(m))

        logging.info('')
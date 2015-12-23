import os
import logging
import pandas as pd

logging.getLogger(__name__)


class Numerai():

    def __enter__(self):
        df = pd.read_csv('../numerai_training_data.csv')
        logging.debug('\n{}'.format(df.head(1)))

        # split
        self.training_set = df[df['validation'] == 0]
        logging.debug('Training set:\n{}'.format(self.training_set.head(1)))

        self.validation_set = df[df['validation'] == 1]
        logging.debug('Validation set:\n{}'.format(self.validation_set.head(1)))

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.debug('exiting')


import argparse
import logging
import time
from sarsa import Sarsa

logging.getLogger(__name__)

MODEL_FILENAME = 'model_plain.dat'
MAX_ITERATIONS = 10

def main(minutes):
    logging.info('training started for {} minutes'.format(minutes))
    logging.info('max iterations: {}'.format(MAX_ITERATIONS))

    # q = loadQ(currency, interval)

    rewards = []
    errors = []
    ticks = []

    start_time = time.time()
    while (time.time() - start_time) < (minutes * 60):

        with Sarsa(MODEL_FILENAME) as sarsa:
            logging.info('sarsa execution')

        # q, r, error, tick = train(df_inner, q, alpha, epsilon, PERIODS, ACTIONS, pip_mul, info['std'])

        break

    #
    #             # results
    #             error *= pip_mul
    #             rewards.append(r)
    #             errors.append(error)
    #             ticks.append(tick)
    #
    #             # win ratio
    #             wins = [1. if r > 0. else 0. for r in rewards]
    #             win_ratio = np.mean(wins)
    #             # logging.error('wr {0}'.format(win_ratio))
    #
    #             # adjust values
    #             alpha = 1.0102052281586786e+000 + (-2.0307383627607809e+000 * win_ratio) + (1.0215546892913909e+000 * win_ratio**2)
    #             epsilon = 3.9851080604500078e-001 + (2.1874724815820201e-002 * win_ratio) + (-4.1444101741886652e-001 * win_ratio**2)
    #             # logging.error('new alpha = {0}'.format(alpha))
    #
    #             # only do updates at interval
    #             if time() - time_start > time_interval or debug:
    #
    #                 # prune lengths
    #                 while len(rewards) > 1000 + minutes * 1000:
    #                     rewards.pop(0)
    #                     errors.pop(0)
    #                     ticks.pop(0)
    #
    #                 # RMSD
    #                 rmsd = np.sqrt(np.mean([e**2 for e in errors]))
    #                 # logging.error('RMSD: {0} from new error {1}'.format(rmsd, error))
    #
    #                 logging.warn('{0} [{1:05d}] RMSD {2:03d} PPT {3:03d} WR {5:.0f}% [ticks:{6:.1f} sum:{4:.1f}, a:{7:.2f}, e:{8:.2f}]'.format(
    #                     currency,
    #                     epoch,
    #                     int(rmsd),
    #                     int(np.mean(rewards) * pip_mul),
    #                     sum(rewards),
    #                     np.mean(wins) * 100,
    #                     np.mean(ticks),
    #                     alpha * 100,
    #                     epsilon * 100,
    #                 ))
    #
    #                 # exit
    #                 if time_interval >= seconds_to_run or debug:
    #                     break
    #
    #                 # continue
    #                 time_interval += seconds_info_intervals
    #                 saveQ(currency, interval, q)
    #
    #         saveQ(currency, interval, q)
    #
    #         summarizeActions(q)
    #
    #         if debug:
    #             break  # currencies
    #
    #     if debug:
    #         break  # forever


########################################################################################################
# SARSA
########################################################################################################


def getAction(q, s, epsilon, actions):
    logging.info('Action: finding...')

    # exploration
    if random() < epsilon:
        logging.debug('Action: explore (<{0:.2f})'.format(epsilon))
        a = choice(actions)

    # exploitation
    else:
        logging.debug('Action: exploit (>{0:.2f})'.format(epsilon))
        q_max = None
        for action in actions:
            q_sa = q.get('|'.join([s, action]), random() * 10.)
            logging.debug('Qsa action {0} is {1:.4f}'.format(action, q_sa))
            if q_sa > q_max:
                q_max = q_sa
                a = action

    logging.info('Action: found {0}'.format(a))
    return a


def getDelta(q, s, a, r):
    logging.info('Delta: calculating...')
    q_sa = q.get('|'.join([s, a]), 0.)
    d = r - q_sa
    # logging.error('Delta: {2:.4f} <= r [{0:.4f}] - Qsa [{1:0.4f}]'.format(r, q_sa, d))
    logging.info('Delta: {0:.4f}'.format(d))
    return d


def updateQ(q, s, a, d, r, alpha):
    logging.info('Q: updating learning at {0:.2f}...'.format(alpha))

    # update q
    sa = '|'.join([s, a])
    q_sa = q.get(sa, 0)
    logging.debug('Q: before {0:.4f}'.format(q_sa))
    q_sa_updated = q_sa + (alpha * d)
    # logging.error('Q: {3:.4f} <= qsa [{0:.4f}] + (alpha [{1:0.3f}] * d [{2:.4f}])'.format(q_sa, alpha, d, q_sa_updated))
    q[sa] = q_sa_updated
    logging.debug('Q: after {0:.4f}'.format(q_sa, q_sa_updated))

    return q


########################################################################################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('minutes')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-vv', '--very_verbose', action='store_true')
    args = parser.parse_args()

    minutes = args.minutes
    verbose = args.verbose
    very_verbose = args.very_verbose
    lvl = logging.DEBUG if very_verbose else (logging.INFO if verbose else logging.WARN)

    logging.basicConfig(
        level=lvl,
        format='%(asctime)s %(levelname)-8s %(name)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    main(minutes)

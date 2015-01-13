class sarsafa():
    # persistant data
    data = []
    weights = []
    graphProfits = []
    ite = 10000
    totalProfits = []
    graphWeights = []

    def updateWeights(self, Fsa, t, a):
        weights = self.weights[a]
        # before = list(weights)
        for i, w in enumerate(weights):
            self.weights[a][i] += (self.alpha * t * Fsa[i])
        # after = self.weights[a]
        # weightsDiff = [abs(a - b) for a, b in zip(before, after)]
        # self.graphWeights.append(weightsDiff)
        # self.log('weights ' + str(before) + ' -> ' + str(after))


    def getReward(self, a, s):
        reward = self.rewards[a][s]
        if self.debug: print 'reward = ' + str(reward)
        return reward



# //////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////
from os import listdir
from os.path import isfile, join, realpath
import json
import pickle
from random import random, choice
from features import *

ACTIONS = ['none', 'short', 'long']
EPSILON = 0.01
GAMMA = 0.99
ALPHA = 0.01


def loadWeights(orderBooks):
    try:
        weights = pickle.load(open("models/weights.dat", "rb"))
    except IOError:
        weights = []
    if len(weights) != len(ACTIONS):
        weights = [[]] * 3
    Fsa = getFsa(orderBooks[orderBooks.keys()[0]])
    for i, data in enumerate(weights):
        if len(data) != len(Fsa):
            weights[i] = [random()] * len(Fsa)
    return weights

def getAction(orderBook, weights, greedyOnly=False):
    # exploitation
    if random() > EPSILON or greedyOnly:
        Qas = []
        Fsa = getFsa(orderBook)
        for a, action in enumerate(ACTIONS):
            Qsa = sum(f * w for f, w in zip(Fsa, weights[a]))
            Qas.append(Qsa)
        QaMax = max(Qas)
        a = Qas.index(QaMax)
    # exploration
    else:
        a = choice(range(len(ACTIONS)))

    return a

def train(orderBooks, weights):
    for timestamp, orderBook in orderBooks.iteritems():
        print 'training', timestamp

        # s, a <- initial state and action of episode
        a = getAction(orderBook, weights)
        print 'action', ACTIONS[a]

        # get reward
        # r = getReward(a, s)

        # # Fa <- set of features present in s, a
        # Fsa = self.getFeatures(s)
        #
        # Qsa = self.getStateValue(Fsa, a)
        #
        # # next state
        # ss = s + 1
        # if ss >= len(self.data):
        #     self.log('next state not in data!')
        #     ss = s
        # self.log('ss = ' + str(ss))
        # aa = self.getAction(ss, True)
        # self.log('aa = ' + str(aa))
        # Fssaa = self.getFeatures(ss, True)
        # Qssaa = self.getStateValue(Fssaa, aa, True)
        #
        # # get theta
        # t = r + (self.gamma * Qssaa) - Qsa
        # self.log('theta = ' + str(t))
        #
        # # update weights
        # self.updateWeights(Fsa, t, a)
        # graphWeights.append(sum(self.weights))

        # if self.debug and i % 100 == 0: raw_input()

    # plt.plot(graphWeights)
    # plt.show()

def saveWeights(self, ite, score):
    print 'saving weights = ' + str(len(self.weights))
    with open(self.currency + '/' + datetime.datetime.now().strftime('%Y%m%d %H%M%S') + ' ' + str(ite) + ' ' + str(score) + '.dat', 'wb') as f:
        pickle.dump(self.weights, f)


def test(features):
    print 'testing'
    # s, a <- initial state and action of episode
    # total = 0
    # for i in range(ite):
    #     r = 0
    #
    #     # s, a <- initial state and action of episode
    #     s = random.randint(1, len(self.data)) - 1
    #     while s <= setTestStart or s >= setTestEnd:
    #         s = random.randint(1, len(self.data)) - 1
    #     self.log('s = ' + str(s))
    #     iniS = s = int(setTestStart)
    #
    #     a = self.getAction(s)
    #     self.log('a = ' + str(a))
    #     iniA = a
    #
    #     while iniA == a:
    #         # next state
    #         ss = s + 1
    #         if ss >= len(self.data):
    #             break
    #             # self.log('next state not in data!')
    #             # ss = s
    #
    #         aa = self.getAction(ss, True, True)
    #
    #         # interim position
    #         closeS = self.closes[iniS]
    #         closeSS = self.closes[s]
    #         if a == 0:
    #             r = 0
    #             # self.log('r = ' + str(total) + ' [none]')
    #         elif a == 1:
    #             r = closeS - closeSS
    #             # self.log('r = ' + str(total) + ' [' + str(closeS) + ' - ' + str(closeSS) + ']')
    #         elif a == 2:
    #             r = closeSS - closeS
    #             # self.log('r = ' + str(total) + ' [' + str(closeSS) + ' - ' + str(closeS) + ']')
    #
    #         # exit
    #         if a != aa:
    #             total += r
    #             iniS = s
    #
    #         self.graphProfits.append(total + r)
    #
    #         s = ss
    #         a = aa
    #
    #     total += r
    #
    # print '\nTotal = ' + str(total)
    #
    # plt.plot(self.graphProfits)
    # plt.show()
    #
    # # if self.debug: raw_input()
    #
    # return total

if __name__ == '__main__':
    pathData = realpath('data/EURUSD')
    onlyfiles = sorted([f for f in listdir(pathData) if isfile(join(pathData, f))])
    data = {}
    for file in onlyfiles:
        with open(pathData + '/' + file, 'rb') as f:
            fileData = json.loads(f.read())
            data = dict(data.items() + fileData.items())
    print 'data loaded'

    orderBooks = extractFeatures(data)
    print 'features extracted'

    orderBooks = calcRewards(orderBooks)
    print 'rewards calculated'
    print orderBooks

    weights = loadWeights(orderBooks)
    print 'weights loaded'

    train(orderBooks, weights)

    pickle.dump(weights, open("models/weights.dat", "wb"))

    test(orderBooks)


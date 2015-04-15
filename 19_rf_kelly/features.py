import pandas as pd
import numpy as np
import sklearn as sk
import scipy as sp
from pprint import pprint


class FeatureFactory():
    def ema(self, s, n):
        """ returns an n period exponential moving average for the time series s
        s is a list ordered from oldest (index 0) to most recent (index -1)
        n is an integer
        returns a numeric array of the exponential moving average """
        s = np.array(s).astype(float)
        ema = []
        j = 1

        # get n sma first and calculate the next n period ema
        sma = sum(s[:n]) / n
        multiplier = 2 / float(1 + n)
        ema[:0] = [sma] * n

        # EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
        ema.append(( (s[n] - sma) * multiplier) + sma)

        # now calculate the rest of the values
        for i in s[n + 1:]:
            tmp = ( (i - ema[j]) * multiplier) + ema[j]
            ema.append(tmp)
            j = j + 1

        # print "ema length = " + str(len(ema))
        return ema


    def rsi(self, closes, n):
        """
        RSI = 100 - 100/(1 + RS*)
        *Where RS = Average of x days' up closes / Average of x days' down closes.
        """
        # print '\ncloses'
        # print len(closes)
        delta = np.diff(closes)
        dUp, dDown = delta.copy(), delta.copy()
        dUp[dUp < 0] = 0
        dDown[dDown > 0] = 0

        RolUp = pd.rolling_mean(dUp, n)
        RolDown = np.absolute(pd.rolling_mean(dDown, n))

        RS = RolUp / RolDown
        RS[0:n-1] = 0
        RS = np.insert(RS, 0, 0)

        # print '\nRS'
        # print len(RS)
        # print RS[0:20]

        rsiCalc = lambda x: 100 - 100 / (1 + x)
        rsi = [rsiCalc(rs) for rs in RS]
        # print '\nrsi'
        # print len(rsi)
        # print np.array(rsi).astype(int)
        return rsi


    def averageTrueRange(self, highs, lows, closes, n):
        '''
        ATR
        '''
        yesterdays = list(closes)
        yesterdays.insert(0, closes[0])
        atr = [max(high - low, abs(high - yesterday), abs(low - yesterday)) for high, low, close, yesterday in zip(highs, lows, closes, yesterdays)]
        atrs = pd.DataFrame(atr)
        atrs = pd.rolling_mean(atrs, n)
        atrs = atrs.fillna(atr[n])
        return atrs.as_matrix()


    def averageDirectionalIndex(self):
        """
        Calculation for Average Directional Index
        TR := SUM(MAX(MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1))),ABS(LOW-REF(CLOSE,1))),N);
        HD := HIGH-REF(HIGH,1);
        LD := REF(LOW,1)-LOW;
        DMP:= SUM(IF(HD>0 & HD>LD,HD,0),N);
        DMM:= SUM(IF(LD>0 & LD>HD,LD,0),N);
        PDI:= DMP*100/TR;
        MDI:= DMM*100/TR;
        ADX:= MA(ABS(MDI-PDI)/(MDI+PDI)*100,N)
        """
        pass


    def getTopsAndBots(self, highs, lows, closes):
        tops, bots = [], []
        for i in xrange(len(highs)):
            hs, ls = [0] * 5, [0] * 5
            close = closes[i]
            for k, n in enumerate([8, 13, 21, 34, 55]):
                start = max(0, i - n) + 1
                # print 'start', start
                end = i + 1
                # print 'end', end
                if end - start < 5:
                    # print 'skipping < 5'
                    continue
                # print len(highs[start:end])
                hs[k] = max(highs[start:end]) / close
                ls[k] = min(lows[start:end]) / close
            # if len(hs):
            #     print hs
            #     print ls
            #     raise Exception('b')
            if len(hs) != 5 or len(ls) != 5:
                raise Exception('get hs and ls has bad lengths')

            tops.append(hs)
            bots.append(ls)

        if len(tops) != len(closes) or len(bots) != len(closes):
            raise Exception('getTopsAndBots has bad lengths')

        return [tops, bots]


    def extractChiMoku(self, highs, lows, closes):
        tenkanSen = []
        kijunSen = []
        senkouSpanB = []
        for i in xrange(len(highs)):
            # avg of highest high and lowest low over past 9 ticks
            tenkanSenHigh = max(highs[max(0, i-9):i+1])
            tenkanSenLow = min(lows[max(0, i-9):i+1])
            tenkanSen.append((tenkanSenHigh + tenkanSenLow) / 2)
            # avg of highest high and lowest low over past 26 ticks
            kijunSenHigh = max(highs[max(0, i-26):i+1])
            kijunSenLow = min(lows[max(0, i-26):i+1])
            kijunSen.append((kijunSenHigh + kijunSenLow) / 2)
            # (Highest high + Lowest low) / 2 over the last 52 trading days plotted 26 days ahead.
            senkouSpanBHigh = max(highs[max(0, i-52):i+1])
            senkouSpanBLow = min(lows[max(0, i-52):i+1])
            senkouSpanB.append((senkouSpanBHigh + senkouSpanBLow) / 2)

        # (Tenkan Sen + Kijun Sen) / 2 plotted 26 days ahead.
        senkouSpanA = [(tenkanSen[0] + kijunSen[0]) / 2] * 256
        senkouSpanA.extend([(t + k) / 2 for t, k in zip(tenkanSen, kijunSen)])
        senkouSpanA = senkouSpanA[:len(highs)]

        # The closing price plotted 26 trading days behind.
        chikouSpan = [closes[0]] * 26
        chikouSpan.extend(closes)
        chikouSpan = chikouSpan[:len(highs)]

        # pprint(tenkanSen[-5:])
        # pprint(kijunSen[-5:])
        # pprint(senkouSpanA)
        return tenkanSen, kijunSen, senkouSpanA, senkouSpanB, chikouSpan


    def getNames(self):
        names = [
            'volume / ema20v', 'volume / ema8v', 'volume / ema5v',
            'ema5v / ema20v', 'ema5v / ema8v',
            'ema8v / ema20v',

            'topShadow / topShadowsMean',
            'body / bodiesMean',
            'bar / barsMean',
            'botShadow / botShadowsMean',

            'top[8]', 'top[13]', 'top[21]', 'top[34]', 'top[55]',
            'bot[8]', 'bot[13]', 'bot[21]', 'bot[34]', 'bot[55]',

            'ema21 / ema34', 'ema34 / ema55', 'ema55 / ema89', 'ema89 / ema144',

            # RSI
            'rsi13', 'rsi21', 'rsi34', 'rsi55',

            'atr21', 'atr34', 'atr55', 'atr89', 'atr144',

            # chimoku
            'tenkanKijunBullishWeak', 'tenkanKijunBullishNeutral', 'tenkanKijunBullishStrong',
            'tenkanKijunBearishWeak', 'tenkanKijunBearishNeutral', 'tenkanKijunBearishStrong',
            'kijunPriceBullishWeak', 'kijunPriceBullishNeutral', 'kijunPriceBullishStrong',
            'kijunPriceBearishWeak', 'kijunPriceBearishNeutral', 'kijunPriceBearishStrong',
            'kumoBullish', 'kumoBearish',
            'senkouSpanBullishWeak', 'senkouSpanBullishNeutral', 'senkouSpanBullishStrong',
            'senkouSpanBearishWeak', 'senkouSpanBearishNeutral', 'senkouSpanBearishStrong',
        ]
        return names


    def getFeatures(self, opens, highs, lows, closes, volumes):
        topShadows = [high - max(open, close) for open, high, close in zip(opens, highs, closes)]
        topShadowsMean = np.mean(topShadows)

        bodies = [abs(open - close) for open, close in zip(opens, closes)]
        bodiesMean = np.mean(bodies)

        bars = [abs(high - low) for high, low in zip(highs, lows)]
        barsMean = np.mean(bars)

        botShadows = [min(open, close) - low for open, low, close in zip(opens, lows, closes)]
        botShadowsMean = np.mean(botShadows)

        tops, bots = self.getTopsAndBots(highs, lows, closes)

        ema5vs = self.ema(volumes, 5)
        ema8vs = self.ema(volumes, 8)
        ema20vs = self.ema(volumes, 20)

        ema21s = self.ema(closes, 21)
        ema34s = self.ema(closes, 34)
        ema55s = self.ema(closes, 55)
        ema89s = self.ema(closes, 89)
        ema144s = self.ema(closes, 144)

        rsi13s = self.rsi(closes, 13)
        rsi21s = self.rsi(closes, 21)
        rsi34s = self.rsi(closes, 34)
        rsi55s = self.rsi(closes, 55)

        atr21s = self.averageTrueRange(highs, lows, closes, 21)
        atr34s = self.averageTrueRange(highs, lows, closes, 34)
        atr55s = self.averageTrueRange(highs, lows, closes, 55)
        atr89s = self.averageTrueRange(highs, lows, closes, 89)
        atr144s = self.averageTrueRange(highs, lows, closes, 144)

        tenkanSen, kijunSen, senkouSpanA, senkouSpanB, chikouSpan = self.extractChiMoku(highs, lows, closes)

        data = [
            [
                volume / ema20v, volume / ema8v, volume / ema5v,
                ema5v / ema20v, ema5v / ema8v,
                ema8v / ema20v,

                topShadow / topShadowsMean,
                body / bodiesMean,
                bar / barsMean,
                botShadow / botShadowsMean,

                top[0], top[1], top[2], top[3], top[4],
                bot[0], bot[1], bot[2], bot[3], bot[4],

                ema21 / ema34, ema34 / ema55, ema55 / ema89, ema89 / ema144,

                rsi13, rsi21, rsi34, rsi55,

                atr21, atr34, atr55, atr89, atr144,

                # TENKAN & KIJUN
                # weak bullish
                1 if tenkanSen > kijunSen and kijunSen < senkouSpanA else 0,
                # neutral bullish
                1 if tenkanSen > kijunSen and senkouSpanA > kijunSen > senkouSpanB else 0,
                # strong bullish
                1 if tenkanSen > kijunSen and kijunSen > senkouSpanA else 0,
                # weak bearish
                1 if tenkanSen < kijunSen and kijunSen > senkouSpanA else 0,
                # neutral bearish
                1 if tenkanSen < kijunSen and senkouSpanA < kijunSen < senkouSpanB else 0,
                # strong bearish
                1 if tenkanSen < kijunSen and kijunSen < senkouSpanA else 0,
                # KIJUN & PRICE
                # weak bullish
                1 if close > kijunSen and kijunSen < senkouSpanA else 0,
                # neutral bullish
                1 if close > kijunSen and senkouSpanA > kijunSen > senkouSpanB else 0,
                # strong bullish
                1 if close > kijunSen and kijunSen > senkouSpanA else 0,
                # weak bearish
                1 if close < kijunSen and kijunSen > senkouSpanA else 0,
                # neutral bearish
                1 if close < kijunSen and senkouSpanA < kijunSen < senkouSpanB else 0,
                # strong bearish
                1 if close < kijunSen and kijunSen < senkouSpanA else 0,
                # KUMO BREAKOUT
                # bullish
                1 if close > senkouSpanA else 0,
                # bearish
                1 if close < senkouSpanA else 0,
                # SENKOU SPAN
                # weak bullish
                1 if senkouSpanA > senkouSpanB and close < senkouSpanA else 0,
                # neutral bullish
                1 if senkouSpanA > senkouSpanB and senkouSpanA > close > senkouSpanB else 0,
                # strong bullish
                1 if senkouSpanA > senkouSpanB and close > senkouSpanA else 0,
                # weak bearish
                1 if senkouSpanA < senkouSpanB and close > senkouSpanA else 0,
                # neutral bearish
                1 if senkouSpanA < senkouSpanB and senkouSpanA < close < senkouSpanB else 0,
                # strong bearish
                1 if senkouSpanA < senkouSpanB and close < senkouSpanA else 0,
            ]
            for close,
                volume, ema5v, ema8v, ema20v,
                topShadow, body, bar, botShadow,
                top, bot,
                ema21, ema34, ema55, ema89, ema144,
                rsi13, rsi21, rsi34, rsi55,
                atr21, atr34, atr55, atr89, atr144,
                tenkanSen, kijunSen, senkouSpanA, senkouSpanB, chikouSpan
            in zip(closes,
                   volumes, ema5vs, ema8vs, ema20vs,
                   topShadows, bodies, bars, botShadows,
                   tops, bots,
                   ema21s, ema34s, ema55s, ema89s, ema144s,
                   rsi13s, rsi21s, rsi34s, rsi55s,
                   atr21s, atr34s, atr55s, atr89s, atr144s,
                   tenkanSen, kijunSen, senkouSpanA, senkouSpanB, chikouSpan
            )
        ]

        # print data
        return data


    def getRewards(self, closes):
        results = []
        iMax = 2
        for pos, close in enumerate(closes):
            tmp = [0]
            for i in xrange(1, iMax):
                index = pos + i
                if index >= len(closes) - 2:
                    break
                tmp.append(closes[index] - close)
            # label = 'long' if sum(tmp) >= 0 else 'short'
            results.append(sum(tmp))
        # pprint(results)

        # mean = np.mean([abs(r) for r in results])
        # mean /= 2
        # print 'mean', round(mean, 4)
        # rewards = ['long' if abs(r) > mean and r > 0 else 'short' if abs(r) > mean and r < 0 else 'none' for r in results]

        rewards = ['long' if r > 0 else 'short' for r in results]
        # pprint(rewards)

        return rewards


    def getSplit(self, data, rewards, shuffle=0):
        X_train, X_test, y_train, y_test = sk.cross_validation.train_test_split(
            data,
            rewards,
            test_size=0.30,
            random_state=shuffle,
        )

        # print '\nScaling features...'
        X_train = sk.preprocessing.scale(X_train)
        X_test = sk.preprocessing.scale(X_test)

        # print 'X-train: ' + str(X_train.shape)
        # print 'y-train: ' + str(y_train.shape)
        # print 'X-test: ' + str(X_test.shape)
        # print 'y-test: ' + str(y_test.shape)

        return [X_train, X_test, y_train, y_test]

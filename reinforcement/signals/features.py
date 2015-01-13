import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score
import sklearn as sk
import operator
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
            'close/ema89', 'close/ema55', 'close/ema34', 'close/ema21', 'close/ema13', 'close/ema08',
            'ema08/ema89', 'ema08/ema55', 'ema08/ema34', 'ema08/ema21', 'ema08/ema13',
            'ema13/ema89', 'ema13/ema55', 'ema13/ema34', 'ema13/ema21',
            'ema21/ema89', 'ema21/ema55', 'ema21/ema34',
            'ema34/ema89', 'ema34/ema55',
            'ema55/ema89',

            # 'volume/ema20v', 'volume/ema8v', 'volume/ema5v',
            # 'ema5v/ema20v', 'ema5v/ema8v',
            # 'ema8v/ema20v',

            'topShadow/topShadowsMean',
            'botShadow/botShadowsMean',

            # RSI
            'close > rsi21', 'close > rsi34', 'close > rsi55', 'rsi21 > rsi34', 'rsi21 > rsi55', 'rsi34 > rsi55',
            'close < rsi21', 'close < rsi34', 'close < rsi55', 'rsi21 < rsi34', 'rsi21 < rsi55', 'rsi34 < rsi55',

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
        ema08s = self.ema(closes, 8)
        ema13s = self.ema(closes, 13)
        ema21s = self.ema(closes, 21)
        ema34s = self.ema(closes, 34)
        ema55s = self.ema(closes, 55)
        ema89s = self.ema(closes, 89)

        # ema5vs = self.ema(volumes, 5)
        # ema8vs = self.ema(volumes, 8)
        # ema20vs = self.ema(volumes, 20)

        topShadows = [high - max(open, close) for open, high, close in zip(opens, highs, closes)]
        topShadowsMean = np.mean(topShadows)

        botShadows = [min(open, close) - low for open, low, close in zip(opens, lows, closes)]
        botShadowsMean = np.mean(botShadows)

        rsi21s = self.rsi(closes, 21)
        rsi34s = self.rsi(closes, 34)
        rsi55s = self.rsi(closes, 55)

        tenkanSen, kijunSen, senkouSpanA, senkouSpanB, chikouSpan = self.extractChiMoku(highs, lows, closes)

        data = [
            [
                # EMA
                close / ema89, close / ema55, close / ema34, close / ema21, close / ema13, close / ema08,
                ema08 / ema89, ema08 / ema55, ema08 / ema34, ema08 / ema21, ema08 / ema13,
                ema13 / ema89, ema13 / ema55, ema13 / ema34, ema13 / ema21,
                ema21 / ema89, ema21 / ema55, ema21 / ema34,
                ema34 / ema89, ema34 / ema55,
                ema55 / ema89,

                # volume / ema20v, volume / ema8v, volume / ema5v,
                # ema5v / ema20v, ema5v / ema8v,
                # ema8v / ema20v,

                topShadow / topShadowsMean,
                botShadow / botShadowsMean,

                # RSI
                # bullish
                1 if close > rsi21 else 0,
                1 if close > rsi34 else 0,
                1 if close > rsi55 else 0,
                1 if rsi21 > rsi34 else 0,
                1 if rsi21 > rsi55 else 0,
                1 if rsi34 > rsi55 else 0,
                # bearish
                1 if close < rsi21 else 0,
                1 if close < rsi34 else 0,
                1 if close < rsi55 else 0,
                1 if rsi21 < rsi34 else 0,
                1 if rsi21 < rsi55 else 0,
                1 if rsi34 < rsi55 else 0,

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
                ema08, ema13, ema21, ema34, ema55, ema89,
                # volume, ema5v, ema8v, ema20v,
                topShadow, botShadow,
                rsi21, rsi34, rsi55,
                tenkanSen, kijunSen, senkouSpanA, senkouSpanB, chikouSpan
            in zip(closes,
                   ema08s, ema13s, ema21s, ema34s, ema55s, ema89s,
                   # volumes, ema5vs, ema8vs, ema20vs,
                   topShadows, botShadows,
                   rsi21s, rsi34s, rsi55s,
                   tenkanSen, kijunSen, senkouSpanA, senkouSpanB, chikouSpan
            )
        ]

        # print data
        return data


    def getRewards(self, closes):
        results = []
        iMax = 5 * 4
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


    def getRewardsCycle(self, closes):
        rewards = []
        iMax = 5 * 4
        for pos, close in enumerate(closes):

            # get score for bull
            bullHighestHigh = close
            bullHighestHighIndex = 0
            for i in range(iMax):
                if pos + i >= len(closes):
                    break
                closeI = closes[pos + i]
                if closeI > bullHighestHigh:
                    bullHighestHigh = closeI
                    bullHighestHighIndex = i

            bullLowestLow = close
            for i in range(bullHighestHighIndex):
                closeI = closes[pos + i]
                bullLowestLow = min([bullLowestLow, closeI])

            bullProfit = bullHighestHigh - close
            bullProfitRel = bullProfit - (close - bullLowestLow)

            # get score for bear
            bearLowestLow = close
            bearLowestLowIndex = 0
            for i in range(iMax):
                if pos + i >= len(closes):
                    break
                closeI = closes[pos + i]
                if close < bearLowestLow:
                    bearLowestLow = closeI
                    bearLowestLowIndex = i

            bearHighestHigh = close
            for i in range(bearLowestLowIndex):
                closeI = closes[pos + i]
                bearHighestHigh = max([bearHighestHigh, closeI])

            bearProfit = close - bearLowestLow
            bearProfitRel = bearProfit - (bearHighestHigh - close)

            rewards.append(bullProfit if bullProfitRel > bearProfitRel else -bearProfit)

        return rewards
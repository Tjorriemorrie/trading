import matplotlib.pyplot as plt


class FeatureFactory():

    def getPeaks(self, df):
        ''' get fibo peaks '''
        startLows, startHighs = [], []
        middleLows, middleHighs = [], []
        sinceLows, sinceHighs, sinceCloses = [], [], []
        m38s, m50s, m61s = [], [], []
        t38s, t61s = [], []
        for i, row in df.iterrows():
            startLow = min(df['low'][max(0, i - 35):max(1, i - 20)])
            startHigh = max(df['high'][max(0, i - 35):max(1, i - 20)])
            startLows.append(startLow)
            startHighs.append(startHigh)
            
            middleLow = min(df['low'][max(0, i - 25):max(1, i - 10)])
            middleHigh = max(df['high'][max(0, i - 25):max(1, i - 10)])
            middleLows.append(middleLow)
            middleHighs.append(middleHigh)
            
            sinceLow = min(df['close'][max(0, i - 15):max(1, i - 0)])
            sinceHigh = max(df['close'][max(0, i - 15):max(1, i - 0)])
            sinceClose = row['close']  # min(df['low'][max(0, i - 13):max(1, i - 0)])
            sinceLows.append(sinceLow)
            sinceHighs.append(sinceHigh)
            sinceCloses.append(sinceClose)

            range = abs(middleHigh - startLow)
            m38 = middleHigh - (range * 0.382)
            m50 = middleHigh - (range * 0.500)
            m61 = middleHigh - (range * 0.618)
            m38s.append(m38)
            m50s.append(m50)
            m61s.append(m61)

            t38 = middleHigh + (range * 0.382)
            t61 = middleHigh + (range * 0.618)
            t38s.append(t38)
            t61s.append(t61)

        df['startLow'] = startLows
        df['startHigh'] = startHighs
        df['middleLow'] = middleLows
        df['middleHigh'] = middleHighs
        df['sinceLow'] = sinceLows
        df['sinceHigh'] = sinceHighs
        df['sinceClose'] = sinceCloses
        df['m38'] = m38s
        df['m50'] = m50s
        df['m61'] = m61s
        df['t38'] = t38s
        df['t61'] = t61s


    def applyEntryFilters(self, df):
        '''apply filters to get entry points'''

        # filter by low since not higher than peak
        df['Fc<p'] = df['sinceLow'] <= df['middleHigh']
        print len(df[df['Fc<p'] == False]), ' lost by Fc<p'

        # LOWS
        # filter: start must be lower than middle low
        df['FsL<mL'] = df['startLow'] <= df['middleLow']
        print len(df[df['FsL<mL'] == False]), ' lost by FsL<mL'
        # filter: end must be lower than middle low
        df['FcL<mL'] = df['sinceLow'] <= df['middleLow']
        print len(df[df['FcL<mL'] == False]), ' lost by FcL<mL'
        lows = df['FsL<mL'] & df['FcL<mL']

        # HIGHS
        # filter by peak of middle must be higher than start
        df['FsP>mP'] = df['middleHigh'] >= df['startHigh']
        print len(df[df['FsP>mP'] == False]), ' lost by FsP>mP'
        # filter by peak of end must be lower than middle
        df['FmP>cP'] = df['middleHigh'] >= df['sinceHigh']
        print len(df[df['FmP>cP'] == False]), ' lost by FmP>cP'
        highs = df['FsP>mP'] & df['FmP>cP']

        # ENTRY
        # filter: low must breach 50
        df['FcL<50'] = df['sinceLow'] < df['m50']
        print len(df[df['FcL<50'] == False]), ' lost by FcL<50'
        # filter: low must not breach 61
        df['FcL>61'] = df['sinceLow'] > df['m61']
        print len(df[df['FcL>61'] == False]), ' lost by FcL>61'
        entry = df['FcL<50'] & df['FcL>61']

        # entry level determined
        df['entry'] = df['Fc<p'] & lows & entry & highs
        print len(df[df['entry'] == True]), ' valid entries!'


    def getEntries(self, df):
        ''' add features to df as columns '''
        self.getPeaks(df)
        self.applyEntryFilters(df)


    def process(self, df):
        '''get exits for where we triggered '''
        trades = []
        entered = False
        for i, row in df.iterrows():
            if row['entry'] and not entered:
                # print 'entering trade!'
                entered = True
                trade = {
                    'entry': row,
                    'entry_index': i,
                }
            # print 'taking loss'
            elif entered and row['close'] < trade['entry']['m61']:
                entered = False
                trade['exit'] = row
                trade['exit_index'] = i
                trade['profit'] = trade['exit']['close'] - trade['entry']['close']
                trades.append(trade)
            # print 'taking profit'
            elif entered and row['close'] > trade['entry']['t38']:
                entered = False
                trade['exit'] = row
                trade['exit_index'] = i
                trade['profit'] = trade['exit']['close'] - trade['entry']['close']
                trades.append(trade)
        return trades


    def showGraphs(self, df, trade):

        iWonEnter = trade['entry_index']
        iWonExit = trade['exit_index']

        dfWonPre = df[max(0, iWonEnter - 54):max(1, iWonEnter - 35)]
        dfWonStart = df[max(0, iWonEnter - 35):max(1, iWonEnter - 20)]
        dfWonMiddle = df[max(0, iWonEnter - 25):max(1, iWonEnter - 10)]
        dfWonEnd = df[max(0, iWonEnter - 15):max(1, iWonEnter - 0)]
        dfWonExit = df[max(0, iWonEnter):max(1, iWonExit)]
        dfWonPost = df[max(0, iWonExit):max(1, iWonExit + 20)]

        # print '\n\n', trade['entry']
        # print 'dfWonStart', len(dfWonStart), dfWonStart['date']
        # print 'dfWonMiddle', len(dfWonMiddle), dfWonMiddle['date']
        # print 'dfWonEnd', len(dfWonEnd), dfWonEnd['date']
        # print tradeWon['exit']

        dfWonPre['close'].plot()
        dfWonStart['close'].plot()
        dfWonMiddle['close'].plot()
        dfWonEnd['close'].plot()
        dfWonExit['close'].plot()
        dfWonPost['close'].plot()
        plt.axhline(y=trade['entry']['m61'], xmin=0, xmax=1, hold=None)
        plt.axhline(y=trade['entry']['m50'], xmin=0, xmax=1, hold=None)
        plt.axhline(y=trade['entry']['t38'], xmin=0, xmax=1, hold=None)
        plt.show()
# Reinforcement learning
---

resistance lines does not work.
let's try reinforcement learning, but the episodes all fit within one day/group.
There will be a penalty if trade is not closed before end of day


## 1. Load data
## 2. Remove outliers as I need a generalized solution.
## 3. Stats: calculate global features now 
## 4. Targets: Get max possible profit for day/group: abs(Highest high - lowest low) (this is already done in outliers)
## 5. Start training (till earliest of trade exit or end of day):
### i. For each tick calculate and add the situational features
### ii. Get available actions 
### iii. Get best action (with epsilon) 
### iv. Get reward for chosen action 
### v. Get next state (calc features) and get action 
### vi. Calculate delta and update thetas 
### vii. Update eligibility traces
## 6. Update rates:
### i. Calculate error
### ii. Update alpha (learning rate) and epsilon (exploration vs exploitation) and gamma (learning range)


## Features

Fuck knows what will be good features.
Let's make everything binary features.
It will need to show:
- out of trade stats; when best to enter
- in trade stats: when best to exit

GOOD
- Add current trade state: waiting, buy, sell, completed
    this will give us Qsa's where we need weights for specific available actions
    this will then not mix weights for entering with exiting
    
- Add progress through group 
    early positive ticks should boost entries, and last positive ticks should boost exits  
    but how many? 24 * 60 = 1440 minutes in day / 15min = 96 groups: thus 100 rounded
    no, we'll trade daily at night, thus daily ticks will be monitored and grouped by month
    
!! remove outliers

- Add trend of exchange rate
    exact values will be useless (especially for binary features)
    which timeframes to add? how can the feature be measured?
    let's just add trend above or below signal line
    let's pick 5/20; we have:
    - ma_crossover_bullish if ma is bullish
    - ma_quick_bullish if quick is going up
    - ma_signal_bullish if signal is going up
    - ma_crossover_divergence if ma gap is increasing
    
- Add pivots
    knowing if price has peaked could help
    wtf, you don't have future data, this peak will be from 2 ticks ago
    
- Add continuations
    this does not mean it's the lowest low/highest high in the group...
    higher highs and lower lows
    3 soldiers as well




- Add monthly move situationals
    firstly, is it at the bottom or top? how do we figure that out? predict it's movement using momentum?
        coz it will then look like it always start in the middle...
    
    
    
BAD
- Add expected range movement left
    this is fucking stupid, we alredy have the progress based on bdays left
        get monthly move mean and std (but only for past year, thus rolling mean the values)
        having past year avg, we can get the range
        but the mean-range is extremely variant, so we have to adjust the predicted-range based on progress of 
            movement during current group
        thus at any state, we get range for tick-to-date, and scale it to expected total number of ticks in group
        thus need to be able to extract for prediction as well
        now we have to see how the rate has moved this month and on a day we can then say it is still at the bottom
            going up, or has moved half the mean-range up or has fully moved up and we can exit buy
        using the adjusted-predicted-range, we can get the required features of:

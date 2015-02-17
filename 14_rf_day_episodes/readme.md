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
- Add progress through group 
    early positive ticks should boost entries, and last positive ticks should boost exits  
    but how many? 24 * 60 = 1440 minutes in day / 15min = 96 groups: thus 100% rounded

BAD
- Add feature for current state for every action
    this won't help, it'll be the same for every action?

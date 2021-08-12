# 0 - sensitivty analysis
# 1 - single RL run
# 2 - optimization
# 3 - mcts trial
# 4 - single RL macro run
pipeline = 4
num_episodes = 1000
############################# RL ########################
# 0 - enemies + round
# 1 - enemies + lands + round
# 2 - enemies + combined threat
# 3 - combined threat + enemies engaged
encoding = 1
default_lr = 0.0001
rlMode = 'lrrrr'

############################# mcts #######################
mctsMode = ['rrrrr']
playoutBudget = 40
playoutsPerSimulation = 1
playoutType = 0 ## 0 - random, 1 - expert

########################## game model ####################
difficulty = 'hard'
fullGame = False
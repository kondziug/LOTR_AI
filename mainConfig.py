# 0 - sensitivty analysis
# 1 - single RL run
# 2 - optimization
# 3 - mcts trial
# 4 - RL macro optimization
# 5 - RLQ macro optimization
pipeline = 1
num_episodes = 1000
############################# RL ########################
# 0 - enemies + round
# 1 - enemies + lands + round
# 2 - enemies + combined threat
# 3 - combined threat + enemies engaged
encoding = 1
default_lr = 0.00005
n_neurons = 100
rlMode = 'llrrr'

############################# mcts #######################
mctsMode = ['rrrrr']
playoutBudget = 40
playoutsPerSimulation = 1
playoutType = 0 ## 0 - random, 1 - expert

########################## game model ####################
difficulty = 'hard'
fullGame = False
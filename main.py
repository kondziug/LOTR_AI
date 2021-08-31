from os import pipe
import simulators
# from Game_Model.game import Game
from defaultAgent import DefaultAgent
import Game_Model.globals
# from envs.lowLevelEnv import LowLevelEnv
# from vanilla_AC.agent import Agent
from vanilla_mcts.mctsAgent import MCTSAgent
from mainConfig import pipeline, num_episodes, n_neurons, default_lr, mctsMode, playoutBudget, playoutsPerSimulation, playoutType
import numpy as np
from itertools import product
import multiprocessing as mp
# import tensorflow as tf
# import logging
# tf.get_logger().setLevel(logging.ERROR)
from hyperopt import tpe, hp, fmin

from simulators.lowLevelSimulator import LowLevelSimulator
from simulators.macroSimulator import MacroSimulator

Game_Model.globals.init()

# best_avg = -1

def sensitivityAnalysis(num_episodes):
    for mode in product('r', repeat=5):
        agent = DefaultAgent(mode, num_episodes)
        rewards = agent.simulate()
        countWins(mode, rewards)

def mctsTrial(params):
    mcts = MCTSAgent(params[0], params[1], params[2], params[3])
    return mcts.simulate()

def countWins(mode, rewards):
    total = 0
    score = 0
    for digit in rewards:
        total += 1
        if digit:
            score += 1
    winrate = score / total * 100
    z = 1.96 # for 95% confidence level
    interv = z * np.sqrt(winrate * (100 - winrate) / total)
    print(f'{mode} winrate: {winrate} ({np.around(interv, decimals=2)})')

def main():
    if pipeline == 0:
        sensitivityAnalysis(num_episodes)
    elif pipeline == 1:
        encoding = 1
        space = { 'lr': default_lr, 'n_neurons': n_neurons }
        simulator = LowLevelSimulator(encoding)
        avg_score = simulator.objective(space)
    elif pipeline == 2:
        encodings = [0, 1, 2, 3]
        for en in encodings:
            simulator = LowLevelSimulator(en)
            space = {
                'lr': hp.loguniform('lr', -10, -7), #### nope
                'n_neurons': hp.choice('n_neurons', [50, 100, 150, 200])
            }
            best = fmin(
                fn=simulator.objective,
                space=space,
                algo=tpe.suggest,
                max_evals=100
            )
            print(best)
    elif pipeline == 3:
        for mode in mctsMode:
            params = []
            for _ in range(num_episodes):
                params.append([mode, playoutBudget, playoutsPerSimulation, playoutType])

            p = mp.Pool()
            rewards = p.map(mctsTrial, params)
            countWins(mode, rewards)
    elif pipeline == 4 or pipeline == 5:
        encodings = [0, 1, 2, 3]
        for en in encodings:
            simulator = MacroSimulator(en)
            space = {
                'lr': hp.loguniform('lr', -10, -7), #### nope
                'n_neurons': hp.choice('n_neurons', [50, 100, 150, 200])
            }
            best = fmin(
                fn=simulator.objective,
                space=space,
                algo=tpe.suggest,
                max_evals=100
            )
            print(best)

if __name__=='__main__':
    main()

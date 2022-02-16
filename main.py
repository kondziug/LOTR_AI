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
import matplotlib.pyplot as plt
from itertools import product
import multiprocessing as mp
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
from hyperopt import tpe, hp, fmin

from simulators.lowLevelSimulator import LowLevelSimulator
from simulators.macroSimulator import MacroSimulator

Game_Model.globals.init() ###### uncomment!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# best_avg = -1

def sensitivityAnalysis(num_episodes):
    # for mode in product('re', repeat=5):
    #     agent = DefaultAgent(mode, num_episodes)
    #     rewards = agent.simulate()
    #     countWins(mode, rewards)
    
    agent = DefaultAgent(mctsMode, num_episodes)
    rewards = agent.simulate()
    success, failHeroes, failThreat = agent.getEpisodeLengths()
    saveEpisodesTotxt(success, failHeroes, failThreat)
    # probs = agent.getDecisionProbs()
    # print(probs)
    # countWins(mctsMode, rewards)


########################################################################

def mctsTrialNuevo(params):
    Game_Model.globals.init()
    mcts = MCTSAgent(params[0], params[1], params[2], params[3])
    return mcts.simulate()

########################################################################
    
def mctsTrial(params):
    mcts = MCTSAgent(params[0], params[1], params[2], params[3])
    return mcts.simulate()

def mctsPlayoutbudget():
    budgets = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    for budget in budgets:    
        params = []
        for _ in range(1000):
            params.append([mctsMode, budget, playoutsPerSimulation, playoutType])

        p = mp.Pool()
        rewards = p.map(mctsTrial, params)
        print(f'Budget: {budget}:')
        countWins(mctsMode, rewards)

def mctsSingleTest(num_episodes):
    params = []
    for _ in range(num_episodes):
        params.append([mctsMode, playoutBudget, playoutsPerSimulation, playoutType])
    p = mp.Pool()
    rewards = []
    successEpisodes = []
    failEpisodes = []
    for reward, success, fail in p.map(mctsTrialNuevo, params):
        rewards.append(reward)
        successEpisodes.append(success)
        failEpisodes.append(fail)

    successEpisodes = [su + 1 for su in successEpisodes if su]
    failEpisodes = [fa + 1 for fa in failEpisodes if fa]
    np.savetxt('successEpisodes.txt', successEpisodes, fmt='%d', newline=' ')
    np.savetxt('failEpisodes.txt', failEpisodes, fmt='%d', newline=' ')

    print(f'Budget: {playoutBudget}:')

    countWins(mctsMode, rewards)

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

def saveEpisodesTotxt(success, failHeroes, failThreat):
    np.savetxt('episodesSuccess.txt', success, fmt='%d', newline=' ')
    np.savetxt('episodesFailHeroes.txt', failHeroes, fmt='%d', newline=' ')
    np.savetxt('episodesFailThreat.txt', failThreat, fmt='%d', newline=' ')

def plotScoreHistory(score_history):
    x = np.arange(100, num_episodes + 1)
    moving_avg = np.convolve(score_history, np.ones(100), 'valid') / 100
    plt.plot(x, moving_avg)
    plt.xlabel('episode')
    plt.ylabel('winrate')
    plt.show()

def plotScoreHistoryFromFile():
    x = np.arange(100, num_episodes + 1)
    x1 = np.arange(1000, num_episodes + 1)
    score_history = np.loadtxt('score_history.txt')
    moving_avg = np.convolve(score_history, np.ones(100), 'valid') / 100
    moving_avg1 = np.convolve(score_history, np.ones(1000), 'valid') / 1000
    plt.plot(x, moving_avg)
    plt.plot(x1, moving_avg1)
    plt.xlabel('episode')
    plt.ylabel('avg_score')
    figName = 'p' + str(pipeline) + 'nn' + str(n_neurons) +'.png'
    plt.savefig(figName)

def main():
    if pipeline == 0:
        sensitivityAnalysis(num_episodes)
    elif pipeline == 1:
        encoding = 1
        space = { 'lr': default_lr, 'n_neurons': n_neurons }
        simulator = LowLevelSimulator(encoding)
        avg_score, score_history = simulator.objective(space)
        # plotScoreHistory(score_history)
    elif pipeline == 2:
        encodings = [0]
        for en in encodings:
            simulator = LowLevelSimulator(en)
            space = {
                # 'lr': hp.loguniform('lrp', -9, -7),
                'lrp': hp.choice('lrp', [3e-4, 3.5e-4, 4e-4, 4.5e-4, 5e-4, 5.5e-4]),
                'lrq': hp.choice('lrq', [6e-4, 6.5e-4, 7e-4, 7.5e-4, 8e-4, 8.5e-4, 9e-4, 1e-3]),
                'n_neurons_p': hp.choice('n_neurons_p', [100, 110, 120, 130, 140, 150, 160]),
                'n_neurons_q': hp.choice('n_neurons_q', [100, 110, 120, 130, 140])
            }
            best = fmin(
                fn=simulator.objective,
                space=space,
                algo=tpe.suggest,
                max_evals=500
            )
            print(best)
    elif pipeline == 3:
        # mctsPlayoutbudget()
        mctsSingleTest(1000)
    elif pipeline == 4 or pipeline == 5:
        encodings = [0]
        for en in encodings:
            simulator = MacroSimulator(en)
            space = {
                'lr': hp.loguniform('lr', -10, -7), #### nope
                'n_neurons': hp.choice('n_neurons', [50, 75, 100, 125, 150])
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

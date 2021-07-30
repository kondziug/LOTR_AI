from Game_Model.game import Game
from environment import Environment
from environment1 import Environment1
from environment2 import Environment2
from defaultAgent import DefaultAgent
import Game_Model.globals
from vanilla_AC.agent import Agent
from vanilla_mcts.mctsAgent import MCTSAgent
from mainConfig import pipeline, num_episodes, encoding, default_lr, mctsMode, playoutBudget, playoutsPerSimulation, playoutType
import numpy as np
from itertools import product
import multiprocessing as mp
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
# from hyperopt import tpe, hp, fmin

Game_Model.globals.init()

best_avg = -1

def sensitivityAnalysis(num_episodes):
    for mode in product('er', repeat=5):
        agent = DefaultAgent(mode, num_episodes)
        rewards = agent.simulate()
        countWins(rewards)

def mctsTrial(params):
    mcts = MCTSAgent(params[0], params[1], params[2], params[3])
    return mcts.simulate()

def countWins(rewards):
    total = 0
    score = 0
    for digit in rewards:
        total += 1
        if digit:
            score += 1
    winrate = score / total * 100
    z = 1.96 # for 95% confidence level
    interv = z * np.sqrt(winrate * (100 - winrate) / total)
    print(f'{mctsMode} winrate: {winrate} ({np.around(interv, decimals=2)})')

def objective(params):
    print(len(Game_Model.globals.decks['Encounter Deck'].cardList))
    print(len(Game_Model.globals.decks['Player Deck'].cardList))

    critic_lr = params['lr']
    actor_lr = params['lr']

    agent_planning = Agent('planning', critic_lr, actor_lr)
    agent_questing = Agent('questing', critic_lr, actor_lr)
    if encoding == 0:
        env = Environment()
    elif encoding == 1:
        env = Environment1()
    elif encoding == 2:
        env = Environment2()
    score_history = []

    for i in range(num_episodes):
        Game_Model.globals.gameWin = False
        Game_Model.globals.gameOver = False
        episode_done = False
        score = 0
        agent_planning.reset()
        agent_questing.reset()
        pobservation = env.reset()
        while not episode_done:
            if len(env.featuresPlanningActor()) != 0:
                agent_planning.setState(env.featuresPlanningActor())

                while True:
                    current_planning_state = env.featuresPlanningActor()
                    if not len(current_planning_state):
                        break
                    current_planning_action = agent_planning.choose_action_planning(current_planning_state)
                    env.step_planning(current_planning_action)
                agent_planning.setAction(env.planning_action)
                next_pobservation = env.featuresPlanningCritic()

            qobservation = env.featuresQuestingCritic()
            if len(env.featuresQuestingActor()) != 0:
                questing_action = agent_questing.choose_action(env.featuresQuestingActor())
                next_qobservation, reward, episode_done = env.step_questing(questing_action)

            env.endRound()

            if Game_Model.globals.gameOver:
                reward = -1
                episode_done = True

            if len(env.featuresPlanningActor()) != 0:
                agent_planning.learn(pobservation, reward, next_pobservation, episode_done)
            if len(env.featuresQuestingActor()) != 0:
                agent_questing.learn(qobservation, reward, next_qobservation, episode_done)

            pobservation = env.featuresPlanningCritic()
            score += reward

        score_history.append(score)

        avg_score = np.mean(score_history[-100:])
        if pipeline == 1 and i % 100 == 0:
            print(f'episode: {i}, avg score: {avg_score}')

    env.hardReset()

    global best_avg
    if avg_score > best_avg and avg_score < 1:
        agent_planning.save_models()
        agent_questing.save_models()
        print('models saved!!!')
        best_avg = avg_score

    return -avg_score

def main():
    if pipeline == 0:
        sensitivityAnalysis(num_episodes)
    elif pipeline == 1:
        space = { 'lr': default_lr }
        avg_score = objective(space)
        print(f'episode: {num_episodes}, avg score: {avg_score}')
    elif pipeline == 2:
        space = {
            'lr': hp.loguniform('lr', -8, -6), #### nope
        }
        best = fmin(
            fn=objective,
            space=space,
            algo=tpe.suggest,
            max_evals=30
        )
        print(best)
    elif pipeline == 3:
        params = []
        for _ in range(num_episodes):
            params.append([mctsMode, playoutBudget, playoutsPerSimulation, playoutType])

        p = mp.Pool()
        rewards = p.map(mctsTrial, params)
        countWins(rewards)

if __name__=='__main__':
    main()

from os import pipe
from Game_Model.game import Game
from defaultAgent import DefaultAgent
import Game_Model.globals
from envs.lowLevelEnv import LowLevelEnv
from vanilla_AC.agent import Agent
from vanilla_mcts.mctsAgent import MCTSAgent
from mainConfig import pipeline, num_episodes, rlMode, encoding, default_lr, mctsMode, playoutBudget, playoutsPerSimulation, playoutType
import numpy as np
from itertools import product
import multiprocessing as mp
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
from hyperopt import tpe, hp, fmin

Game_Model.globals.init()

best_avg = -1

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

def objective(params):
    print(len(Game_Model.globals.decks['Encounter Deck'].cardList))
    print(len(Game_Model.globals.decks['Player Deck'].cardList))

    critic_lr = params['lr']
    actor_lr = params['lr']

    if rlMode[0] == 'l': agent_planning = Agent('planning', 2, critic_lr, actor_lr)
    if rlMode[1] == 'l': agent_questing = Agent('questing', 2, critic_lr, actor_lr)
    env = LowLevelEnv(encoding)
    score_history = []

    for i in range(num_episodes):
        Game_Model.globals.gameWin = False
        Game_Model.globals.gameOver = False
        episode_done = False
        score = 0
        if rlMode[0] == 'l': agent_planning.reset()
        if rlMode[1] == 'l': agent_questing.reset()
        pobservation = env.reset()
        while not episode_done:
            ###################### Planning #######################
            if rlMode[0] == 'l':
                if len(env.encoder.encodePlanning('actor')) != 0:
                    agent_planning.setState(env.encoder.encodePlanning('actor'))

                    while True:
                        current_planning_state = env.encoder.encodePlanning('actor')
                        if not len(current_planning_state):
                            break
                        current_planning_action = agent_planning.choose_action_planning(current_planning_state)
                        env.step_planning(current_planning_action)
                    agent_planning.setAction(env.planning_action)
                    next_pobservation = env.encoder.encodePlanning('critic')
            else:
                env.game.randomPlanning()
                reward = 0
                
            ###################### Questing ########################
            if rlMode[1] == 'l':
                qobservation = env.encoder.encodeQuesting('critic')
                if len(env.encoder.encodeQuesting('actor')) != 0:
                    questing_action = agent_questing.choose_action(env.encoder.encodeQuesting('actor'))
                    next_qobservation, reward, episode_done = env.step_questing(questing_action)
            elif rlMode[1] == 'e':
                env.game.expertQuesting()
                reward = 0
            else:
                env.game.randomQuesting()
                reward = 0

            env.endRound(rlMode)

            if Game_Model.globals.gameWin:
                reward = 1
                episode_done = True
            if Game_Model.globals.gameOver and not Game_Model.globals.gameWin:
                reward = -1
                episode_done = True
            

            if rlMode[0] == 'l' and len(env.encoder.encodePlanning('actor')) != 0:
                agent_planning.learn(pobservation, reward, next_pobservation, episode_done)
            if rlMode[1] == 'l' and len(env.encoder.encodeQuesting('actor')) != 0:
                agent_questing.learn(qobservation, reward, next_qobservation, episode_done)

            pobservation = env.encoder.encodePlanning('critic')
            score += reward

        score_history.append(score)

        avg_score = np.mean(score_history[-100:])
        if pipeline == 1 and i % 100 == 0:
            print(f'episode: {i}, avg score: {avg_score}')

    env.hardReset()

    global best_avg
    if avg_score > best_avg and avg_score < 1:
        if rlMode[0] == 'l': agent_planning.save_models()
        if rlMode[1] == 'l': agent_questing.save_models()
        print(f'models saved with best avg: {avg_score}')
        best_avg = avg_score

    return -avg_score

def objectiveMacro(params):
    from macroEnv import MacroEnv
    from vanilla_q.agent import QAgent
    # print(len(Game_Model.globals.decks['Encounter Deck'].cardList))
    # print(len(Game_Model.globals.decks['Player Deck'].cardList))

    critic_lr = params['lr']
    actor_lr = params['lr']

    if rlMode[0] == 'l' and pipeline == 4: agent_planning = Agent('planning', 3, critic_lr, actor_lr)
    if rlMode[0] == 'l' and pipeline == 5: agent_planning = QAgent('planning', 3, params['lr'])
    if rlMode[1] == 'l' and pipeline == 4: agent_questing = Agent('questing', 3, critic_lr, actor_lr)
    if rlMode[1] == 'l' and pipeline == 5: agent_questing = QAgent('questing', 3, params['lr'])
    env = MacroEnv()
    score_history = []

    for i in range(num_episodes):
        Game_Model.globals.gameWin = False
        Game_Model.globals.gameOver = False
        episode_done = False
        score = 0
        if rlMode[0] == 'l': agent_planning.reset()
        if rlMode[1] == 'l': agent_questing.reset()
        pobservation = env.reset()
        while not episode_done:
            ###################### Planning #######################
            if rlMode[0] == 'l':
                if len(env.featuresPlanning()) != 0:
                    planning_action = agent_planning.choose_action(pobservation)
                    next_pobservation = env.step_planning(planning_action)      
            else:
                env.game.randomPlanning()
                reward = 0
                
            ###################### Questing ########################
            if rlMode[1] == 'l':
                qobservation = env.featuresQuesting()
                if len(env.featuresQuesting()) != 0:
                    questing_action = agent_questing.choose_action(qobservation)
                    next_qobservation, reward, episode_done = env.step_questing(questing_action)
            elif rlMode[1] == 'e':
                env.game.expertQuesting()
                reward = 0
            else:
                env.game.randomQuesting()
                reward = 0

            env.endRound(rlMode)

            if Game_Model.globals.gameWin:
                reward = 1
                episode_done = True
            if Game_Model.globals.gameOver and not Game_Model.globals.gameWin:
                reward = -1
                episode_done = True
            

            if rlMode[0] == 'l' and pipeline == 4 and len(next_pobservation) != 0:
                agent_planning.learn(pobservation, reward, next_pobservation, episode_done)
            if rlMode[0] == 'l' and pipeline == 5 and len(next_pobservation) != 0:
                agent_planning.learn(planning_action[0], pobservation, reward, next_pobservation)
            if rlMode[1] == 'l' and pipeline == 4 and len(next_qobservation) != 0:
                agent_questing.learn(qobservation, reward, next_qobservation, episode_done)
            if rlMode[1] == 'l' and pipeline == 5 and len(next_qobservation) != 0:
                agent_questing.learn(questing_action[0], qobservation, reward, next_qobservation)

            pobservation = env.featuresPlanning()
            score += reward

        score_history.append(score)

        avg_score = np.mean(score_history[-100:])
        if (pipeline == 4 or pipeline == 5) and i % 100 == 0:
            print(f'episode: {i}, avg score: {avg_score}')

    env.hardReset()

    global best_avg
    if avg_score > best_avg and avg_score < 1:
        if rlMode[0] == 'l': agent_planning.save_models()
        if rlMode[1] == 'l': agent_questing.save_models()
        print(f'models saved with best avg: {avg_score}')
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
        for mode in mctsMode:
            params = []
            for _ in range(num_episodes):
                params.append([mode, playoutBudget, playoutsPerSimulation, playoutType])

            p = mp.Pool()
            rewards = p.map(mctsTrial, params)
            countWins(mode, rewards)
    elif pipeline == 4 or pipeline == 5:
        space = { 'lr': default_lr }
        avg_score = objectiveMacro(space)
        print(f'episode: {num_episodes}, avg score: {avg_score}')

if __name__=='__main__':
    main()

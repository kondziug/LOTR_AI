from environment import Environment
from environment1 import Environment1
from environment2 import Environment2
from environment3 import Environment3
import Game_Model.globals
from vanilla_AC.agent import Agent
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
from main import countWins
from mainConfig import difficulty

Game_Model.globals.init()

num_episodes = 10000

filename = 'llrrr-hard-en3-test'

def main():
    if filename[0] == 'l':
        agent_planning = Agent('planning')
        agent_planning.load_models(filename, 'planning')
    if filename[1] == 'l':
        agent_questing = Agent('questing')
        agent_questing.load_models(filename, 'questing')
    env = Environment3() ############### set appriopriate env along with filename !!!!!!!!
    score_history = []

    for i in range(num_episodes):
        Game_Model.globals.gameWin = False
        Game_Model.globals.gameOver = False
        episode_done = False
        score = 0
        if filename[0] == 'l': agent_planning.reset()
        if filename[1] == 'l': agent_questing.reset()
        pobservation = env.reset()
        while not episode_done:
            ########################### Planning #####################
            if filename[0] == 'l':
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
            else:
                env.game.randomPlanning()
                reward = 0

            if filename[1] == 'l':
                qobservation = env.featuresQuestingCritic()
                if len(env.featuresQuestingActor()) != 0:
                    questing_action = agent_questing.choose_action(env.featuresQuestingActor())
                    next_qobservation, reward, episode_done = env.step_questing(questing_action)
            else:
                env.game.randomQuesting()
                reward = 0
            
            env.endRound(filename)

            if Game_Model.globals.gameOver:
                reward = 0
                episode_done = True
            if Game_Model.globals.gameWin:
                reward = 1
                episode_done = True

            pobservation = env.featuresPlanningCritic()
            score += reward

        score_history.append(score)

    countWins(filename[:5], score_history)


if __name__=='__main__':
    main()

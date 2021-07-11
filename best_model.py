from environment import Environment
import Game_Model.globals
from vanilla_AC.agent import Agent
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)

Game_Model.globals.init()

num_episodes = 10000

def main():
    agent_planning = Agent('planning')
    agent_questing = Agent('questing')
    agent_planning.load_models()
    agent_questing.load_models()
    env = Environment()
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

            pobservation = env.featuresPlanningCritic()
            score += reward

        score_history.append(score)

    avg_score = np.mean(score_history)
    print(f'episodes: {num_episodes}, avg score: {avg_score}')


if __name__=='__main__':
    main()

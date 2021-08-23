import numpy as np
from simulators.baseSimulator import BaseSimulator
from vanilla_AC.agent import Agent
from vanilla_q.agent import QAgent
from mainConfig import pipeline, rlMode

class MacroSimulator(BaseSimulator):
    def __init__(self):
        super(MacroSimulator, self).__init__()
        self.agent_p = None
        self.agent_q = None

    def agent_planning(self):
        return self.agent_p

    def agent_questing(self):
        return self.agent_q

    def setAgents(self, params):
        if rlMode[0] == 'l':
            if pipeline == 4: self.agent_p = Agent('planning', 7, params['lr'], params['lr'])
            elif pipeline == 5: self.agent_p = QAgent('planning', 7, params['lr'])
        if rlMode[1] == 'l':
            if pipeline == 4: self.agent_q = Agent('questing', 7, params['lr'], params['lr'])
            elif pipeline == 5: self.agent_q = QAgent('questing', 7, params['lr'])
        
    def rlPlanning(self, observation):
        if len(self.env.encoder.encodePlanning('macro')) != 0:
            action = self.agent_p.choose_action(observation)
            next_observation = self.env.step_planning(action) 
            return action, next_observation

    def rlQuesting(self):
        observation = self.env.encoder.encodeQuesting('macro')
        if len(observation) != 0:
            action = self.agent_q.choose_action(observation)
            next_observation, reward, episode_done = self.env.step_questing(action)
            return observation, action, next_observation, reward, episode_done
        return observation, None, self.env.encoder.encodeQuesting('macro'), 0, False 

    def learnPlanning(self, observation, action, reward, next_observation, episode_done):
        if len(next_observation) != 0:
            if pipeline == 4:
                self.agent_p.learn(observation, reward, next_observation, episode_done)
            elif pipeline == 5:
                self.agent_p.learn(action[0], observation, reward, next_observation)

    def learnQuesting(self, observation, action, reward, next_observation, episode_done):
        if len(next_observation) != 0:
            if pipeline == 4:
                self.agent_q.learn(observation, reward, next_observation, episode_done)
            elif pipeline == 5:
                self.agent_q.learn(action[0], observation, reward, next_observation)
    
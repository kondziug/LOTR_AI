from os import pipe
import numpy as np
from abc import ABC, abstractmethod, abstractproperty
import Game_Model.globals
from envs.lowLevelEnv import LowLevelEnv
from envs.macroEnv import MacroEnv
from mainConfig import pipeline, rlMode, num_episodes, difficulty

class BaseSimulator(ABC):
    def __init__(self, encoding):
        self.encoding = encoding
        self.env = None
        self.setEnv()
        self.best_global_avg = -1

    @property
    @abstractmethod
    def agent_planning(self):
        pass

    @abstractproperty
    def agent_questing(self):
        pass

    @abstractmethod
    def setAgents(self, params):
        pass

    def setEnv(self):
        if pipeline == 1 or pipeline == 2:
            self.env = LowLevelEnv(self.encoding)
        elif pipeline == 4 or pipeline == 5:
            self.env = MacroEnv(self.encoding)

    @abstractmethod
    def rlPlanning(self, observation): # returns planning_action, next_pobservation
        pass

    @abstractmethod
    def rlQuesting(self): # returns observation, action, next_observation, reward, episode_done
        pass

    def simulatePlanning(self, observation):
        if rlMode[0] == 'l':
            return self.rlPlanning(observation)
        self.env.game.randomPlanning()
        return None, None

    def simulateQuesting(self):
        if rlMode[1] == 'l':
            return self.rlQuesting()
        self.env.game.randomQuesting()
        return None, None, None

    @abstractmethod
    def learnPlanning(self, observation, action, reward, next_observation, episode_done):
        pass

    @abstractmethod
    def learnQuesting(self, observation, action, reward, next_observation, episode_done):
        pass

    def objective(self, params):
        self.setAgents(params)

        best_local_avg = -1
        score_history = []

        for i in range(num_episodes):
            Game_Model.globals.gameWin = False
            Game_Model.globals.gameOver = False
            episode_done = False
            score = 0
            if rlMode[0] == 'l': self.agent_planning().reset()
            if rlMode[1] == 'l': self.agent_questing().reset()
            pobservation = self.env.reset()
            while not episode_done:
                reward = 0
                planning_action, next_pobservation = self.simulatePlanning(pobservation)
                    
                qobservation, questing_action, next_qobservation, reward, episode_done = self.simulateQuesting()

                self.env.endRound(rlMode)

                if Game_Model.globals.gameWin:
                    reward = 1
                    episode_done = True
                if Game_Model.globals.gameOver and not Game_Model.globals.gameWin:
                    reward = -1
                    episode_done = True
                
                if rlMode[0] == 'l': self.learnPlanning(pobservation, planning_action, reward, next_pobservation, episode_done)
                if rlMode[1] == 'l': self.learnQuesting(qobservation, questing_action, reward, next_qobservation, episode_done)

                pobservation = self.env.encoder.encodePlanning('critic')
                score += reward

            score_history.append(score)

            avg_score = np.mean(score_history[-1000:])
            if i % 100 == 0 and i > 1000:
                if avg_score > best_local_avg:
                    best_local_avg = avg_score
                if best_local_avg > self.best_global_avg and pipeline != 1:
                    nn = params['n_neurons']
                    lr = params['lr']
                    dirname = rlMode + 'p' + str(pipeline) + 'en' + str(self.encoding) + 'nn' + str(nn) + difficulty
                    if rlMode[0] == 'l': self.agent_planning().save_models(dirname, 'planning')
                    if rlMode[1] == 'l': self.agent_questing().save_models(dirname, 'questing')
                    print(f'model with {nn} neurons, lr: {lr} saved with best global avg: {self.best_global_avg}')
                    self.best_global_avg = best_local_avg

                # print(f'episode: {i}, avg score: {avg_score}')
                    

        self.env.hardReset()

        print(f'best local avg: {best_local_avg}')
        if pipeline == 1:
            return best_local_avg, score_history
        return -best_local_avg

    def loadAndTest(self, params):
        self.setAgents(params)
        dirname = rlMode + 'p' + str(pipeline) + 'en' + str(self.encoding) + 'nn' + str(params['n_neurons']) + difficulty
        if rlMode[0] == 'l': self.agent_planning().load_models(dirname, 'planning')
        if rlMode[1] == 'l': self.agent_questing().load_models(dirname, 'questing')

        score_history = []

        for i in range(num_episodes):
            Game_Model.globals.gameWin = False
            Game_Model.globals.gameOver = False
            episode_done = False
            score = 0
            if rlMode[0] == 'l': self.agent_planning().reset()
            if rlMode[1] == 'l': self.agent_questing().reset()
            pobservation = self.env.reset()
            while not episode_done:
                reward = 0
                self.simulatePlanning(pobservation)
                    
                self.simulateQuesting()

                self.env.endRound(rlMode)

                if Game_Model.globals.gameWin:
                    reward = 1
                    episode_done = True
                if Game_Model.globals.gameOver and not Game_Model.globals.gameWin:
                    reward = 0
                    episode_done = True
                
                pobservation = self.env.encoder.encodePlanning('critic')
                score += reward

            score_history.append(score)

        return score_history


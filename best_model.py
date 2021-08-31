import os
from simulators.lowLevelSimulator import LowLevelSimulator
from simulators.macroSimulator import MacroSimulator
import Game_Model.globals
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
from main import countWins
from mainConfig import pipeline, rlMode, difficulty, encoding


def main():
    dirNames = os.listdir('results')
    dirNames = [k for k in dirNames if rlMode in k and 'p' + str(pipeline) in k and 'en' + str(encoding) in k and difficulty in k]
    for dirName in dirNames:
        Game_Model.globals.init()
        n_neurons = dirName[12:15]
        n_neurons = n_neurons if not n_neurons[-1].isalpha() else n_neurons[0:2]
        params = { 'lr': 0.0001, 'n_neurons': int(n_neurons) }
        if pipeline == 1 or pipeline == 2: env = LowLevelSimulator(encoding)
        if pipeline == 4 or pipeline == 5: env = MacroSimulator(encoding)
        score_history = env.loadAndTest(params)
        countWins(dirName, score_history)

if __name__=='__main__':
    main()

import os
from simulators.lowLevelSimulator import LowLevelSimulator
from simulators.macroSimulator import MacroSimulator
import Game_Model.globals
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
from main import countWins
from mainConfig import pipeline, rlMode, difficulty, encoding

## only for double learning rate!!!!

def main():
    dirName = 'llrrrp2en2nn100hard'
    Game_Model.globals.init()
    n_neurons = dirName[12:15]
    n_neurons = n_neurons if not n_neurons[-1].isalpha() else n_neurons[0:2]
    params = { 'lrp': 0.0001, 'lrq': 0.0001, 'n_neurons': 150 }
    if pipeline == 1 or pipeline == 2: env = LowLevelSimulator(encoding)
    if pipeline == 4 or pipeline == 5: env = MacroSimulator(encoding)
    score_history = env.loadAndTest(params)
    countWins(dirName, score_history)

if __name__=='__main__':
    main()

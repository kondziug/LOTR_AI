from simulators.lowLevelSimulator import LowLevelSimulator
from simulators.macroSimulator import MacroSimulator
import Game_Model.globals
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)
from main import countWins
from mainConfig import pipeline, rlMode, n_neurons, difficulty

Game_Model.globals.init()

def main():
    encoding = 1
    if pipeline == 1 or pipeline == 2: env = LowLevelSimulator(encoding)
    if pipeline == 4 or pipeline == 5: env = MacroSimulator(encoding)
    score_history = env.loadAndTest()
    dirname = rlMode + 'p' + str(pipeline) + 'en' + str(encoding) + 'nn' + str(n_neurons) + difficulty
    countWins(dirname, score_history)


if __name__=='__main__':
    main()

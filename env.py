import portfolio
import numpy as np
import chart
import utils

class Env():

    def __init__(self, symbols,env_type):
        self.index = 0 # basically counts as counter 
        self.symbols = symbols
        self.portfolio = portfolio.portolio(self.symbols,env_type)
        self.timesteps = 5

        self.port_values = np.ones((1000,1)) *0.1
        self.port_diffs = np.zeros((1000,len(self.symbols)))
        self.actions = np.zeros((1000,len(self.symbols)))
        self.chart_obj = chart.Chart(self.symbols)

        self.mean, self.std = utils.read_from_csv(dir = 'G:\\My Drive\\Models\\chartStats\\')
        self.threshold = 0
        self.current_value = None
    
    def reset(self):
        _ = self.portfolio.reset()
        self.action_dict = {}
        self.port_values = np.ones((1000,1)) *0.1
        self.port_diffs = np.zeros((1000,len(self.symbols)))
        self.actions = np.zeros((1000,len(self.symbols)))
        self.index = 5
        self.chart,self.og_chart = self.chart_obj.process()
        self.chart_len,self.cols = self.chart.shape
        state = self.get_recurrent_state(self.index)
        return state

    def get_recurrent_state(self, index):
        
        sequence = self.chart[index-self.timesteps:index]
        sequence = (sequence - self.mean)/self.std
        sequence = np.reshape(sequence, (1,self.timesteps,self.cols))

        port_values = self.port_values[index-self.timesteps:index]
        port_sequence = np.reshape(port_values, (1,self.timesteps,1))

        port_diffs_values = self.port_diffs[index-self.timesteps:index]
        port_diff_sequence = np.reshape(port_diffs_values, (1,self.timesteps,len(self.symbols)))

        state = np.concatenate((port_sequence,sequence,port_diff_sequence), axis=2).astype(np.float64)

        return state  

    def calculate_reward(self,action):
        action_dict = dict(zip(self.symbols, np.squeeze(action)))
        self.close_prices = {}
        for symbol in self.symbols:
            self.close_prices[symbol] = self.og_chart[symbol]['close'].iloc[-1] # Last close value from original chart
        
        port_diffs, current_value = self.portfolio.update_value(close_values = self.close_prices, actions = action_dict)
        self.current_value = current_value
        self.port_values[self.index] = current_value * 0.1
        self.port_diffs[self.index] = np.array(list(port_diffs.values()))
    
    def step(self, action):
        self.calculate_reward(action)
        done = False

        if ((self.port_values[self.index] < self.threshold*0.1)):
            done = True
            print('done')

        next_state = self.get_recurrent_state(self.index)
        self.index += 1

        return next_state, done



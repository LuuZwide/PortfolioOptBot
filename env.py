import portfolio
import numpy as np
import chart
import utils
from datetime import datetime
import os
import meta
import json

class Env():

    def __init__(self, symbols,env_type):
        self.index = 0 # basically counts as counter 
        self.symbols = symbols
        self.portfolio = portfolio.portfolio(self.symbols,env_type)
        self.timesteps = 4

        self.port_values = np.zeros((1000,1)) 
        self.port_diffs = np.zeros((1000,len(self.symbols)))
        self.actions = np.zeros((1000,len(self.symbols)))
        self.chart_obj = chart.Chart(self.symbols)
        self.value = 1

        self.mean, self.std = utils.read_from_csv(dir = './info/ChartStats/')
        self.threshold = 0.4#Live threshold - take the L start tomorrow 
        self.current_value = 0
        self.action_dict = {}

    
    def reset(self, load_from = 'R'):
        # R -> Reset
        # T -> Today
        # Y -> Yesterday

        self.action_dict = {}
        yesterday = utils.get_previous_weekday(datetime.now()).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        dir = './info/PortfolioStats/' + today + '/'

        if load_from == 'T' : #today
            dir = './info/PortfolioStats/' + today + '/'
            print('Loading from today dir : ', dir)
            self.load_state(dir)
            _ = self.portfolio.reset( dir, True, 'T')
        elif load_from == 'Y' : #Yesterday
            dir = './info/PortfolioStats/' + yesterday + '/'
            print('Loading from yesterday dir : ', dir)
            self.load_state(dir)
            _ = self.portfolio.reset( dir, True, 'Y')
        else:
            self.port_values = np.zeros((1000,1))
            self.port_diffs = np.zeros((1000,len(self.symbols)))
            self.actions = np.zeros((1000,len(self.symbols)))
            self.index = self.timesteps # Start at the timestep index
            _ = self.portfolio.reset( dir, False)
            meta.close_all(self.symbols)
        
        self.chart,self.og_chart = self.chart_obj.process()
        self.chart_len,self.cols = self.chart.shape
        state = self.get_recurrent_state(self.index)
        return state

    def get_recurrent_state(self, index):
        
        sequence = self.chart[-1-self.timesteps:-1]
        sequence = (sequence - self.mean)/self.std
        sequence = np.reshape(sequence, (1,self.timesteps,self.cols))

        port_values = self.port_values[index-self.timesteps:index]
        port_sequence = np.reshape(port_values, (1,self.timesteps,1))

        port_diffs_values = self.port_diffs[index-self.timesteps:index]
        port_diff_sequence = np.reshape(port_diffs_values, (1,self.timesteps,len(self.symbols)))

        state = np.concatenate((port_sequence,sequence,port_diff_sequence), axis=2).astype(np.float64)

        return state  

    def calculate_reward(self,action):
        self.action_dict = dict(zip(self.symbols, np.squeeze(action)))
        self.close_prices = {}
        for symbol in self.symbols:
            self.close_prices[symbol] = self.og_chart[symbol]['close'].iloc[-1] # Last close value from original chart
        
        port_diffs, current_value = self.portfolio.update_value(close_values = self.close_prices, actions = self.action_dict )
        self.current_value = current_value
        self.value = self.portfolio.value
        self.port_values[self.index] = np.log(current_value) if current_value > 0 else np.log(1e-1)
        self.port_diffs[self.index] = np.array(list(port_diffs.values()))
    
    def step(self, action):
        
        self.chart,self.og_chart = self.chart_obj.process()
        self.calculate_reward(action)
        done = False

        if ((self.value < self.threshold)):
            done = True
            print('__________done_______________')
            meta.close_all(self.symbols)

        next_state = self.get_recurrent_state(self.index)
        self.index += 1

        return next_state, done
    
    def save_env(self):
        today = datetime.now().strftime("%Y-%m-%d")
        dir = './info/PortfolioStats/' + today + '/'
        #If directory does not exist create it
        if not os.path.exists(dir):
            os.makedirs(dir)

        self.save_state(dir)
        self.portfolio.save_values(dir)

        return
    
    def save_state(self, dir):
        env_dic = {
            'index': self.index,
            'current' : self.current_value,
            'port_values': self.port_values.tolist(),
            'port_diffs': self.port_diffs.tolist(),
            'actions': self.actions.tolist()
        }
        try:
            with open(dir + 'env.json', 'w') as f:
                json.dump(env_dic, f)
            return
        except FileNotFoundError:
            with open(dir + 'env.json', 'w') as f:
               json.dump(env_dic, f)
        return  
    
    def load_state(self, dir):
        try:
            with open(dir + 'env.json', 'r') as f:
                env_dic = json.load(f)
                self.index = env_dic['index']
                self.current_value = env_dic['current']
                self.port_values = np.array(env_dic['port_values'])
                self.port_diffs = np.array(env_dic['port_diffs'])
                self.actions = np.array(env_dic['actions'])
        except FileNotFoundError:
            print("Env file not found. Starting with default values.")
            self.reset()
        return
    

 
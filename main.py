from sb3_contrib import RecurrentPPO
import env
from stable_baselines3 import PPO
import numpy as np
import utils
import pandas as pd
import meta
import MetaTrader5 as mt5
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--user', type=str, default='demo', help='User type: demo or live')
parser.add_argument('--start_from', type=str, default='R', help='R: Reset, T: Today, Y: Yesterday')
args = parser.parse_args()

p_user = args.user
p_start_from = args.start_from

# R -> Reset - starts new run 
# T -> Today - loads todays data incase of crash
# Y -> Yesterday - loads from yesterday

if __name__ == "__main__":
    symbols = ['EURUSD', 'USDJPY', 'EURJPY']

    logins_dir = "./info/Credentials"
    username, password, server = utils.get_logins(dir = logins_dir, user = p_user)
    meta.login(username, password, server)
    
    env_type = 'QA'
    env = env.Env(symbols,env_type)

    print('mean', env.mean)
    print('std', env.std)
    model = RecurrentPPO.load("./info/Models/best_model.zip")
    env.reset(load_from = p_start_from) 
    done = False
    '''
        working hours 00:02 from Monday to Friday
    '''

    #wait till 02:02 then start
    utils.wait_until_time("02:02")

    while not (done):
        state = env.return_current_state()
        action, _ = model.predict(state, deterministic=True)
        done = env.step(action)
        # Debug msg
        print('closing prices', env.close_prices)
        print('actions : ', env.action_dict)
        print('%',env.portfolio.percentage_diff_dict)
        print('env current_value: ', env.current_value)
        print('env port value : ', env.value)
        print('Equity :', mt5.account_info().equity) # type: ignore
        
        print('\n')
        env.save_env()

        if done:
            break
        else:
            #wait for next 15min candle
            utils.wait_until_next_interval(15)
import env
from stable_baselines3 import PPO
import numpy as np
import utils
import pandas as pd
import meta
import MetaTrader5 as mt5
import stable_baselines3

print(np.__version__)
print(pd.__version__)
print(stable_baselines3.__version__)

# P = _n7wRxUo
# U = 95713077 

if __name__ == "__main__":
    symbols = ['EURUSD', 'USDCHF', 'EURJPY', 'USDJPY']
    
    user = 'demo' # demo or LIVE
    logins_dir = r"C:\Users\LNxumalo\Desktop\other\Docs"
    username, password, server = utils.get_logins(dir = logins_dir, user = user)
    meta.login(username, password, server)
    
    env_type = 'QA'
    env = env.Env(symbols,env_type)
    model = PPO.load(r'G:\My Drive\Models\SB3\rec_best_model\best_model.zip')
    state = env.reset(load_from = 'R') 
        # R -> Reset
        # T -> Today
        # Y -> Yesterday
    done = False
    '''
        working hours 07:00 to 19:45 UTC
        Pretoria times 09:00 to 21:45 (UTC + 2)
    '''

    #wait till 09:00 then start
    utils.wait_until_time("09:00")

    while not (done):
        action, _ = model.predict(state, deterministic=True)
        action_dict = dict(zip(symbols, np.squeeze(action)))
        state, done= env.step(action)
        # Debug msg
        print('closing prices', env.close_prices)
        print('%',env.portfolio.percentage_diff_dict.values())
        print('env current_value: ', env.current_value)
        print('Equity :', mt5.account_info().equity) # type: ignore
        print('\n')
        env.save_env()
        
        if utils.stop_if_time("21:45"):
            break
        else:
            utils.wait_minute(15,10) #15 minutes 10 seconds




    
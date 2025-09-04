import numpy as np
import pywt
import pandas as pd
from datetime import datetime, timedelta
import time
import json

def wavelet_denoise(data, wavelet='db4'):
    coeffs = pywt.wavedec(data, wavelet)
    cA, *details = coeffs

    # Estimate noise from the first detail level
    D = details[-1]  # Finest scale detail coefficients
    N = len(D)
    median_abs_D = np.median(np.abs(D))
    T = (np.sqrt(2 * np.log(N)) * median_abs_D) / 0.6745

    # Soft-thresholding
    def soft_thresh(d, T):
        return np.sign(d) * np.maximum(np.abs(d) - T, 0)

    details_thresh = [soft_thresh(d, T) for d in details]
    coeffs_thresh = [cA] + details_thresh

    # Reconstruct signal
    return pywt.waverec(coeffs_thresh, wavelet)

def normlise_time(df):
  return df.hour / 24 + df.minute / 1440 + df.second / 86400

def calculate_macd_sma_ema(data, short_window=12, long_window=26, signal_window=9, sma_window=10, ema_window=10,sc_window=10):

    #Ensure data is a pandas Series
    prices = pd.Series(data['close'], name="close") # Oldest to Newest
    low_prices = pd.Series(data['low'], name="low")
    high_prices = pd.Series(data['high'], name="high")

    # Calculate MACD
    ema_short = prices.ewm(span=short_window, adjust=False).mean()
    ema_long = prices.ewm(span=long_window, adjust=False).mean()
    macd = ema_short - ema_long
    signal = macd.ewm(span=signal_window, adjust=False).mean()

    # Calculate SMA from the back
    sma_back = prices.rolling(window=sma_window).mean()

    # Calculate EMA from the back
    ema_back = prices.ewm(span=ema_window, adjust=False).mean()

    #Stochastic occilator
    low_14 = low_prices.rolling(window=sc_window).min()
    high_14 = high_prices.rolling(window=sc_window).max()
    stoch_k = 100 * ((prices - low_14) / (high_14 - low_14))
    stoch_d = stoch_k.rolling(window=3).mean()

    # Combine all results into a DataFrame
    result_df = pd.DataFrame({
        "close": prices,
        #"Low": low_prices,
        #"High": high_prices,
        "SMA": sma_back,
        "EMA": ema_back,
        "MACD": macd,
        "Signal": signal,
        "Histogram": macd - signal,
        "Stoch_k": stoch_k,
        "Stoch_d": stoch_d
    })

    return result_df

def wait_minute(minutes,seconds ):
    now = datetime.now()
    next_minute = (now + timedelta(minutes = minutes)).replace(second = seconds , microsecond = 0)
    sleep_time = (next_minute - now).total_seconds()
    time.sleep(sleep_time)

def get_logins(dir,user):
    dir = dir
    if user == 'demo':
        main_dir = dir + '\demo_logins.csv' # type: ignore
    elif user == 'live':
        main_dir = dir + '\live_logins.csv' # type: ignore
    else:
        print('invalid : enter demo or live')
        return None,None,None
    login_df = pd.read_csv(main_dir, delimiter=';')
    logins_array = login_df.values[0]
    username = logins_array[0]
    password = logins_array[1]
    server = logins_array[2]
    return username, password, server

# P = _n7wRxUo
# U = 95713077

def write_to_csv(mean, std, dir):
    mean_df = pd.DataFrame(mean)
    std_df = pd.DataFrame(std)
    
    #write to csv
    mean_df.to_csv(dir + 'mean.csv', index=False)
    std_df.to_csv(dir + 'std.csv', index=False)
    
    return 

def read_from_csv(dir):
    mean_df = pd.read_csv(dir + 'mean.csv')
    std_df = pd.read_csv(dir + 'std.csv')
    
    mean = mean_df.values
    std = std_df.values
    
    mean = mean.flatten()
    std = std.flatten()
    return mean, std

def wait_until_time(target_time):
    while True:
        now = datetime.now()
        if now.strftime("%H:%M") > target_time:
            break
        time.sleep(1)

def stop_if_time(target_time):
    now = datetime.now()
    if now.strftime("%H:%M") > target_time:
        print("Ending session : ", now)
        return True
    else:
        return False

def save_actions(actions, dir):
    #Create folder for today
    actions_df = pd.DataFrame(actions)
    actions_df.to_csv(dir + 'actions.csv', index=False)
    return

def save_port_values(port_values, dir):
    port_values_df = pd.DataFrame(port_values)
    port_values_df.to_csv(dir + 'port_values.csv', index=False)
    return

def save_portfolio_diffs(portfolio_diffs, dir):
    portfolio_diffs_df = pd.DataFrame(portfolio_diffs)
    portfolio_diffs_df.to_csv(dir + 'portfolio_diffs.csv', index=False)
    return

def save_index(index, dir):
    index_df = pd.DataFrame([index])
    index_df.to_csv(dir + 'index.csv', index=False)
    return

def load_env_values(dir):
    actions = pd.read_csv(dir + 'actions.csv').values
    port_values = pd.read_csv(dir + 'port_values.csv').values
    portfolio_diffs = pd.read_csv(dir + 'portfolio_diffs.csv').values
    index = pd.read_csv(dir + 'index.csv').values
    index = np.squeeze(index)
    print('loaded index ', index)
    print('port values :', port_values.shape)
    print('portfolio diffs :', portfolio_diffs.shape)
    print('loaded actions :', actions.shape)
    print('Current port value :', port_values[index -1])

    return actions, port_values, portfolio_diffs, index

def get_previous_weekday(date):
    #IF yesterday was Sunday get Friday
    if date.weekday() == 0:  # Monday
        previous_weekday = date - timedelta(days=3)
    else:
        previous_weekday = date - timedelta(days=1)
    return previous_weekday

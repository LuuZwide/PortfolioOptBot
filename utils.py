import numpy as np
import pywt
import pandas as pd
from datetime import datetime, timedelta
import time


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
        main_dir = dir + '\demo_logins.csv'
    elif user == 'live':
        main_dir = dir + '\live_logins.csv'
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
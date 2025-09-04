# This class - loads data from polygon 
# Transforms data into chart
# outputs chart data

# Main function is return_current_chart as a vector not DICT
# checks date a symbols
# returns the latest chart info for all symbols

# Other functions
# 1. Get latest candels from polygon for all symbols
# 2. Transform data using wavelet transform
# 3. add stat values 

# Process
# For each symbol in symbols:
#   Get latest data from polygon - convert datetime (oldest to newest) asc order
#   denoise data
#   On last symbol add data column
#   Drop na records
#   add to dict 
#
# Return vector not dict
import pandas as pd
from datetime import datetime, timedelta
from polygon import RESTClient
import utils
import numpy as np

FOREX_CLIENT = RESTClient("Y_MQfuWV7a5mqIVZeIiB4Y7P4Z9FrpRq")

class Chart():
    def __init__(self, symbols):

        self.symbols = symbols

    def process(self):
        chart_dict = {}
        original_chart_dict = {}
        for symbol in self.symbols:
            symbol_chart = self.get_polygon_chart(symbol = symbol) # Return latest chart Data
            #print(symbol_chart)

            #Perform the preprocessing functions 
            denoised_chart = self.perform_wavelet_denoise(symbol_chart)

            processed_chart = utils.calculate_macd_sma_ema(denoised_chart,sma_window=20, ema_window=9, sc_window=14)
            processed_chart.dropna(inplace=True)

            #if last symbol add time
            if (symbol == self.symbols[-1]):
                size = len(processed_chart['close'])
                processed_chart['date'] = symbol_chart['date'].apply(utils.normlise_time).values[:size]            
            
            #Drop the na rows
            processed_chart.dropna(inplace=True)
            processed_chart.reset_index(drop=True, inplace=True)

            #add to chart dict
            chart_dict[symbol] = processed_chart
            original_chart_dict[symbol] = symbol_chart
        
        #Concatenate 
        state_chart = pd.concat(chart_dict,axis=1)
        state_chart = state_chart.dropna().values
        state_chart = state_chart.astype(np.float64)

        return state_chart , original_chart_dict
            
    
    def get_polygon_chart(self, symbol = None):
        today = datetime.today()
        chart_to_date = today.strftime('%Y-%m-%d') # to today
        chart_from_date = today - timedelta(days=(5)) #From Yesterday
        chart_from_date = chart_from_date.strftime('%Y-%m-%d')
        df = self.generateCandleSticks(client=FOREX_CLIENT, start_date = chart_from_date, end_date = chart_to_date, limit = 5000, symbol = symbol )
        return df

    def generateCandleSticks(self,client, start_date  , end_date ,limit , symbol= None):
        symbol = 'C:' + symbol # type: ignore
        response =  client.get_aggs(ticker = symbol ,multiplier = 15,timespan = 'minute',
                                  from_= start_date, to = end_date, sort = 'asc',limit = limit) # Oldest -> Latest
        
        df = pd.DataFrame(response)
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        #Only keep times between 07:00 and 19:45 UTC
        df = df[(df['date'].dt.time >= datetime.strptime("07:00", "%H:%M").time()) & (df['date'].dt.time <= datetime.strptime("19:45", "%H:%M").time())]
        final_df = df[[ 'open', 'high', 'low', 'close','date']]
        print(symbol,final_df.values[-1] )
        return final_df
    
    def perform_wavelet_denoise(self, chart):
        denoised_chart = {}
        denoised_chart['close'] = utils.wavelet_denoise(chart['close'].values)
        denoised_chart['low'] = utils.wavelet_denoise(chart['low'].values)
        denoised_chart['high'] = utils.wavelet_denoise(chart['high'].values)
        denoised_chart_df = pd.DataFrame(denoised_chart)
        denoised_chart_df = denoised_chart_df.astype(np.float64)
        return denoised_chart_df       
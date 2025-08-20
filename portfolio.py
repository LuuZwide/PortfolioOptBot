
import meta

class portolio():

    def __init__(self,symbols, env_type):
        self.symbols = symbols
        self.leverage = 200
        self.bought =  dict.fromkeys(symbols, False)
        self.bought_values = {}
        self.percentage_diff_dict = dict.fromkeys(symbols, 0)
        self.selling = dict.fromkeys(symbols, False)
        self.percentage_diff_dict = {}
        self.port_changes = {}
        self.selling_values = {}
        self.threshold_value = 0.1
        self.updating = dict.fromkeys(symbols, False)
        self.meta_symbols = meta.get_meta_symbols(symbols,env_type)
        self.counter = 0


    def calculate_returns(self,close_price, type, bought_value,selling_value):
        if (type == 'S'):
            percentage_diff = (selling_value - close_price)/selling_value
        if (type == 'B'):
            percentage_diff = (close_price - bought_value)/bought_value
        
        percentage_diff = percentage_diff * 100
        port_change =  percentage_diff * self.leverage
        return port_change, percentage_diff
    
    def add_spread(self,close_price ):
        bid_price = close_price * (1 + 0.0001)
        ask_price = close_price * (1 - 0.0001)
        return  bid_price, ask_price
    
    def update_value(self, close_values, actions):
        for symbol in self.symbols:
            percentage_diff = 0
            self.counter += 1

            close_value = close_values[symbol]
            action = actions[symbol]

            if (action > self.threshold_value) and self.bought[symbol]: #Update port
                bought_value  = self.bought_values[symbol]
                percentage_diff, port_change = self.calculate_returns(close_value, 'B',bought_value, -1)
                self.port_changes[symbol] = 0
                self.percentage_diff_dict[symbol] = percentage_diff

            if (action < -1*self.threshold_value) and self.selling[symbol]: #Update port
                selling_value = self.selling_values[symbol]
                percentage_diff, port_change = self.calculate_returns(close_value, 'S', -1 ,selling_value)
                self.port_changes[symbol] = 0
                self.percentage_diff_dict[symbol] = percentage_diff

            if (action > self.threshold_value) and not self.bought[symbol]: # First buy
                if self.selling[symbol]:#Close the sell trade
                    self.selling[symbol] = False
                    selling_value = self.selling_values[symbol]
                    percentage_diff, port_change = self.calculate_returns(close_value, 'S', -1, selling_value)
                    self.value += percentage_diff
                    self.port_changes[symbol] = port_change
                    self.percentage_diff_dict[symbol] = 0               
                    #Meta
                    meta.closePositions(self.meta_symbols[symbol])
                else:
                    self.bought[symbol] = True
                    self.bought_values[symbol], _ = self.add_spread(close_value)
                    bought_value = self.bought_values[symbol]
                    percentage_diff, port_change = self.calculate_returns(close_value, 'B', bought_value, -1 )
                    self.port_changes[symbol] = 0
                    self.percentage_diff_dict[symbol] = percentage_diff

                    meta.BUY(self.meta_symbols[symbol],self.counter)       

            if (action < -1*self.threshold_value) and not self.selling[symbol] : # First Sell
                if self.bought[symbol]: #Close the buy trade
                    self.bought[symbol] = False
                    bought_value = self.bought_values[symbol]
                    percentage_diff, port_change = self.calculate_returns(close_value, 'B', bought_value, -1)
                    self.value += percentage_diff
                    self.port_changes[symbol] = port_change
                    self.percentage_diff_dict[symbol] = 0
                    meta.closePositions(self.meta_symbols[symbol])
                else:
                    self.selling[symbol] = True
                    _, self.selling_values[symbol] = self.add_spread(close_value)
                    selling_value = self.selling_values[symbol]
                    percentage_diff, port_change = self.calculate_returns(close_value, 'S', -1 , selling_value)
                    self.port_changes[symbol] = 0
                    self.percentage_diff_dict[symbol] = percentage_diff  
                    meta.SELL(self.meta_symbols[symbol],self.counter)

            if ((action < self.threshold_value) and (action > -1*self.threshold_value)) and self.bought[symbol]: # Close the buy
                bought_value = self.bought_values[symbol]
                percentage_diff, port_change = self.calculate_returns(close_value, 'B',bought_value,-1)
                self.value += percentage_diff
                self.port_changes[symbol] = port_change
                self.percentage_diff_dict[symbol] = 0
                self.bought[symbol] = False
                self.selling[symbol] = False   
                meta.closePositions(self.meta_symbols[symbol])   

            if ((action < self.threshold_value) and  (action > -1*self.threshold_value)) and self.selling[symbol]: #Close the sell
                self.closed = True
                selling_value = self.selling_values[symbol]
                percentage_diff, port_change = self.calculate_returns(close_value, 'S',-1,selling_value)
                self.value += percentage_diff
                self.port_changes[symbol] = port_change
                self.percentage_diff_dict[symbol] = 0
                self.selling[symbol] = False
                self.bought[symbol] = False       
                meta.closePositions(self.meta_symbols[symbol]) 

        sum_percentage_diff = sum(self.percentage_diff_dict.values())
        current_value = self.value + sum_percentage_diff

        return self.percentage_diff_dict, current_value    
    
    def reset(self):
        self.value = 1
        self.flying_value = 1
        self.trade_counter = 0
        self.bought_values = {}
        self.selling_values = {}
        self.updating = False
        self.closed = False
        self.updating = dict.fromkeys(self.symbols, False)
        self.non_trades = 0
        self.percentage_diff_dict = dict.fromkeys(self.symbols, 0)
        self.bought = dict.fromkeys(self.symbols, False)
        self.b_counter = 0
        self.s_counter = 0
        self.selling = dict.fromkeys(self.symbols, False)
        return self.value
import MetaTrader5 as mt5
import utils

def login(username, password, server, retry_count = 0):
        username = username
        password = password
        server = server
        print('username : ', username)
        print('password : ', password)
        print('server : ', server)

        if not mt5.initialize(login=username, server=server,password=password):
              print("login failed, error code =",mt5.last_error())
              quit()
        else: 
              #Set equity values only if this is the first start
              if (retry_count == 0):
                    initial_equity = mt5.account_info().equity
                    print('Equity set to :', initial_equity)

def get_meta_symbols(symbols, env_type):
    meta_symbols = {}
    for symbol in symbols:
        if env_type.upper() == 'LIVE':
            meta_symbol = symbol + 'm'
        else:
            meta_symbol = symbol
        meta_symbols[symbol] = meta_symbol
    return meta_symbols
               

def do_test(symbols, env_type):
    meta_symbols = get_meta_symbols(symbols, env_type)
    for symbol in symbols:
        
        if not mt5.symbol_select(meta_symbols[symbol], True):
            print(f"Failed to select {meta_symbols[0]}, error code =", mt5.last_error())
            return False
        else:
            tick_info = mt5.symbol_info_tick(meta_symbols[symbol])  
            if tick_info:
                print('Passed Connection...')
                return True
            else:
                print(f"Failed to get tick info for {meta_symbols[symbol]}, error code =", mt5.last_error())   
                return False

def can_act(self):
    #check equity
    current_equity = mt5.account_info().equity
    can_act = True
    threshold = self.threshold_percent * self.initial_equity
    
    #First Test ... we can add more test 
    # Like limit of steps and shit....
    if(current_equity < threshold):
          print('Equity Threshold broken!!.....')
          can_act = False
    return can_act

def retry(env_type,symbols,username, password,server,fail_count):
    if(fail_count < 5):
        #Increase fail count
        fail_count += 1     
        
        #login and test
        login(username, password,server,fail_count)
        result = do_test(symbols,env_type)
        return result

def closePositions(symbol):
        positions = mt5.positions_get(symbol=symbol)
        if positions != None:  
              for position in positions:
                    position_id = position.ticket
                    print('Postion Type :',position.type)
                    mt5.Close(symbol,ticket=position_id)
        return

def getRequest(type, price,magic,symbol, volume = 0.01,deviation = 20): 
    request = {
        "action"        : mt5.TRADE_ACTION_DEAL,
        "magic"         : magic + 1,
        "symbol"        : symbol,
        "volume"        : volume,
        "price"         : price,
        "type"          : type,
        "deviation"     : deviation ,
        "type_time"     : mt5.ORDER_TIME_GTC,
        "type_filling"  : mt5.ORDER_FILLING_IOC, 
        "comment"       : "This is a test order ",   
    }
    return request

def BUY(symbol, counter):
    type = mt5.ORDER_TYPE_BUY
    print('symbol : ', symbol)
    price = mt5.symbol_info_tick(symbol).ask 
    request = getRequest(type,price, counter, symbol)
    result = mt5.order_send(request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("order failed , retcode = {}".format(result.retcode))
        utils.wait_minute(minutes = 1, seconds = 10)
         
    return price 

def SELL(symbol, counter):
    type = mt5.ORDER_TYPE_SELL
    print('symbol : ', symbol)
    price = mt5.symbol_info_tick(symbol).ask 
    request = getRequest(type,price, counter, symbol)
    result = mt5.order_send(request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("order failed , retcode = {}".format(result.retcode))
        utils.wait_minute(minutes = 1, seconds = 10)

    return price



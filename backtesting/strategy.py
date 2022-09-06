import talib as ta
from backtesting import Backtest, Strategy
from lib import crossover, cross
from util import *
import numpy as np

def name2strategy(name_list):
  name2strategy_dict = {'MACD_Cross':MACD_Cross,'SMA_Cross':SMA_Cross,'EMA_Cross':EMA_Cross,'DEMA_Cross':DEMA_Cross,'RSI':RSI,'BolingerBands':BolingerBands,'InsideBar':InsideBar,'OutsideBar':OutsideBar}
  return [name2strategy_dict[name] for name in name_list]
  
def close_opposite_dir_trade(trade_list,dir):
  for trade in trade_list:
    if trade.size * dir <= 0: #size and dir has diff. direction
      trade.close()
 
def get_trade_num(trade_list,dir):
  return len([1 for trade in trade_list if trade.size * dir > 0])
  
def dSMA(price,period=39):
  sma = ta.SMA(price,period)
  return (price-sma)/sma*100
  
class dSMA_Cross(Strategy):
  name = 'dSMA_Cross'
  param_size = 1-1e-10
  param_period = 30
  param_directed = 0
  
  def init(self):
    close = self.data.Close
    self.sma = self.I(ta.SMA, close, self.param_period)
    self.dsma = self.I(dSMA, close, self.param_period)
    return self.sma, self.dsma
  
  def buy_condition(self):
    return crossover(self.dsma, 0)
    
  def sell_condition(self):
    return crossover(0, self.dsma)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)

class SMA_Cross(Strategy):
  name = 'SMA_Cross'
  param_size = 1-1e-10
  param_fastperiod = 10
  param_slowperiod = 20
  param_directed = 0
  
  def init(self):
    close = self.data.Close
    self.sma1 = self.I(ta.SMA, close, self.param_fastperiod)
    self.sma2 = self.I(ta.SMA, close, self.param_slowperiod)
    return self.sma1,self.sma2
  
  def buy_condition(self):
    return crossover(self.sma1, self.sma2)
    
  def sell_condition(self):
    return crossover(self.sma2, self.sma1)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      
class EMA_Cross(Strategy):
  name = 'EMA_Cross'
  param_size = 1-1e-10
  param_fastperiod = 10
  param_slowperiod = 20
  param_directed = 0
  
  def init(self):
    close = self.data.Close
    self.ema1 = self.I(ta.EMA, close, self.param_fastperiod)
    self.ema2 = self.I(ta.EMA, close, self.param_slowperiod)
    return self.ema1,self.ema2
  
  def buy_condition(self):
    return crossover(self.ema1, self.ema2)
    
  def sell_condition(self):
    return crossover(self.ema2, self.ema1)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      
class EMA_Cross_3Line(Strategy):
  name = 'EMA_Cross_3Line'
  param_size = 1-1e-10
  param_period1 = 10
  param_period2 = 20
  param_period3 = 30
  param_directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.ema1 = self.I(ta.EMA, close, self.param_period1)
    self.ema2 = self.I(ta.EMA, close, self.param_period2)
    self.ema3 = self.I(ta.EMA, close, self.param_period3)
    return self.ema1,self.ema2,self.ema3
  
  def buy_condition(self):
    return all([self.data.Close[-1] > ema[-1] for ema in [self.ema1,self.ema2,self.ema3]]) and any([crossover(self.data.Close, ema) for ema in [self.ema1,self.ema2,self.ema3]])
    
  def sell_condition(self):
    return all([self.data.Close[-1] < ema[-1] for ema in [self.ema1,self.ema2,self.ema3]]) and any([crossover(ema, self.data.Close) for ema in [self.ema1,self.ema2,self.ema3]])
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True

class EMA_Cross_4Line(Strategy):
  name = 'EMA_Cross_4Line'
  param_size = 1-1e-10
  param_period1 = 10
  param_period2 = 20
  param_period3 = 30
  param_period4 = 40
  param_directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.ema1 = self.I(ta.EMA, close, self.param_period1)
    self.ema2 = self.I(ta.EMA, close, self.param_period2)
    self.ema3 = self.I(ta.EMA, close, self.param_period3)
    self.ema4 = self.I(ta.EMA, close, self.param_period4)
    return self.ema1,self.ema2,self.ema3
  
  def buy_condition(self):
    return all([self.data.Close[-1] > ema[-1] for ema in [self.ema1,self.ema2,self.ema3,self.ema4]]) and any([crossover(self.data.Close, ema) for ema in [self.ema1,self.ema2,self.ema3,self.ema4]])
    
  def sell_condition(self):
    return all([self.data.Close[-1] < ema[-1] for ema in [self.ema1,self.ema2,self.ema3,self.ema4]]) and any([crossover(ema, self.data.Close) for ema in [self.ema1,self.ema2,self.ema3,self.ema4]])
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True

class WMA_Cross(Strategy):
  name = 'WMA_Cross'
  param_size = 1-1e-10
  param_fastperiod = 10
  param_slowperiod = 20
  param_directed = 0
  
  def init(self):
    close = self.data.Close
    self.wma1 = self.I(ta.WMA, close, self.param_fastperiod)
    self.wma2 = self.I(ta.WMA, close, self.param_slowperiod)
    return self.wma1,self.wma2
  
  def buy_condition(self):
    return crossover(self.wma1, self.wma2)
    
  def sell_condition(self):
    return crossover(self.wma2, self.wma1)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      
class DEMA_Cross(Strategy):
  name = 'DEMA_Cross'
  param_size = 1-1e-10
  param_fastperiod = 10
  param_slowperiod = 20
  param_directed = 0
  
  def init(self):
    close = self.data.Close
    self.dema1 = self.I(ta.DEMA, close, self.param_fastperiod)
    self.dema2 = self.I(ta.DEMA, close, self.param_slowperiod)
    return self.dema1,self.dema2
  
  def buy_condition(self):
    return crossover(self.dema1, self.dema2)
    
  def sell_condition(self):
    return crossover(self.dema2, self.dema1)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      
class TEMA_Cross(Strategy):
  name = 'TEMA_Cross'
  param_size = 1-1e-10
  param_fastperiod = 10
  param_slowperiod = 20
  param_directed = 0
  
  def init(self):
    close = self.data.Close
    self.tema1 = self.I(ta.TEMA, close, self.param_fastperiod)
    self.tema2 = self.I(ta.TEMA, close, self.param_slowperiod)
    return self.tema1,self.tema2
  
  def buy_condition(self):
    return crossover(self.tema1, self.tema2)
    
  def sell_condition(self):
    return crossover(self.tema2, self.tema1)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      
class TRIMA_Cross(Strategy):
  name = 'TRIMA_Cross'
  param_size = 1-1e-10
  param_fastperiod = 10
  param_slowperiod = 20
  param_directed = 0
  
  def init(self):
    close = self.data.Close
    self.trima1 = self.I(ta.TRIMA, close, self.param_fastperiod)
    self.trima2 = self.I(ta.TRIMA, close, self.param_slowperiod)
    return self.trima1,self.trima2
  
  def buy_condition(self):
    return crossover(self.trima1, self.trima2)
    
  def sell_condition(self):
    return crossover(self.trima2, self.trima1)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)

class RSI(Strategy):
  name = 'RSI'
  param_size = param_size = 1-1e-10
  param_timeperiod = 14
  param_overbought = 60
  param_oversold = 30
  param_delay = 1
  param_directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.rsi = self.I(ta.RSI, close, self.param_timeperiod)
    return self.rsi
  
  def buy_condition(self):
    return self.rsi[-(self.param_delay+1)] > self.param_oversold and all([self.rsi[-i] < self.param_oversold for i in range(1,self.param_delay+1)])
    #return all([self.rsi[-i] < self.param_oversold for i in range(1,self.param_delay+1)])  
    
  def sell_condition(self):
    return self.rsi[-(self.param_delay+1)] < self.param_overbought and all([self.rsi[-i] > self.param_overbought for i in range(1,self.param_delay+1)])
    #return all([self.rsi[-i] > self.param_overbought for i in range(1,self.param_delay+1)])
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True

class MACD_Cross(Strategy):
  name = 'MACD_Cross'
  param_size = 1-1e-10
  param_fastperiod = 12
  param_slowperiod = 26
  param_signalperiod = 9
  param_directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.macd, self.macdsignal, self.macdhisyt = self.I(ta.MACD,close, self.param_fastperiod, self.param_slowperiod, self.param_signalperiod)
    return self.macd, self.macdsignal, self.macdhisyt
  
  def buy_condition(self):
    return crossover(self.macd, self.macdsignal)
    
  def sell_condition(self):
    return crossover(self.macdsignal, self.macd)
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True
      
class BarUpDown(Strategy):
  name = "BarUpDown"
  param_size = 1-1e-10
  param_max_loss = 1
  param_directed = 0
  pre_equity = np.nan
  long_pos = False
  short_pos = False
  
  def init(self):
    pass
    
  def buy_condition(self):
    return self.data.Close[-1] > self.data.Open[-1] and self.data.Open[-1] > self.data.Close[-2]
    
  def sell_condition(self):
    return self.data.Close[-1] < self.data.Open[-1] and self.data.Open[-1] < self.data.Close[-2]
  
  def next(self):
    if self.pre_equity != np.nan:
      stop_loss = self.equity < self.pre_equity*(1-self.param_max_loss/100)
      long_pos = False
      short_pos = False
    else:
      stop_loss = False
    self.pre_equity = self.equity
    
    if stop_loss:
      [trade.close() for trade in self.trades]
    
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True

class ChannelBreakOut(Strategy):
  name = "ChannelBreakOut"
  param_size = 1-1e-10
  param_length = 5
  param_directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    pass
    
  def buy_condition(self):
    high = self.data.High
    upbound = np.max([high[-(self.param_length+1):-1]])
    return upbound < high[-1]
    
  def sell_condition(self):
    low = self.data.Low
    downbound = np.min([low[-(self.param_length+1):-1]])
    return downbound > low[-1]
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True
      
class InsideBar(Strategy):
  name = "InsideBar"
  param_size = 1-1e-10
  param_directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    pass
    
  def buy_condition(self):
    return self.data.High[-1] < self.data.High[-2] and self.data.Low[-1] > self.data.Low[-2] and self.data.Close[-1] > self.data.Open[-1]
    
  def sell_condition(self):
    return self.data.High[-1] < self.data.High[-2] and self.data.Low[-1] > self.data.Low[-2] and self.data.Close[-1] < self.data.Open[-1]
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True
      
class OutsideBar(Strategy):
  name = "OutsideBar"
  param_size = 1-1e-10
  param_directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    pass
    
  def buy_condition(self):
    return self.data.High[-1] > self.data.High[-2] and self.data.Low[-1] < self.data.Low[-2] and self.data.Close[-1] > self.data.Open[-1]
    
  def sell_condition(self):
    return self.data.High[-1] > self.data.High[-2] and self.data.Low[-1] < self.data.Low[-2] and self.data.Close[-1] < self.data.Open[-1]
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True
      
class Momentum(Strategy):
  name = "InsideBar"
  param_size = 1-1e-10
  param_length = 12
  param_directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.mom0 = self.I(ta.MOM,close,self.param_length)
    self.mom1 = self.I(ta.MOM,self.mom0, 1)
    return self.mom0, self.mom1
    
  def buy_condition(self):
    return self.mom0 > 0 and self.mom1 > 0
    
  def sell_condition(self):
    return self.mom0 < 0 and self.mom1 < 0
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    #elif not self.buy_condition() and self.long_pos:
    #  close_opposite_dir_trade(self.trades,dir=0)
    #  self.long_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True
    #elif not self.sell_condition() and self.short_pos:
    #  close_opposite_dir_trade(self.trades,dir=0)
    #  self.short_pos = False
      
class ConsecutiveUpDown(Strategy):
  name = "ConsecutiveUpDown"
  param_size = 1-1e-10
  param_barsup = 3
  param_barsup = 3
  param_directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    pass
    
  def buy_condition(self):
    close = self.data.Close
    try:
      consup = np.all(close[-(self.param_barsup+1):-1] < close[-self.param_barsup:])
    except:
      consup = False #in case of first step of iteration
    return consup
    
  def sell_condition(self):
    close = self.data.Close
    try:
      consdown = np.all(close[-(self.param_barsup+1):-1] > close[-self.param_barsup:])
    except:
      consdown = False
    return consdown
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True
      

class BolingerBands(Strategy):
  name = 'BolingerBands'
  param_size = 1-1e-10
  param_timeperiod = 20
  param_nbdevup = 2
  param_nbdevdn = 2
  param_directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.upperband, self.middleband, self.lowerband = self.I(ta.BBANDS,close, self.param_timeperiod, self.param_nbdevup, self.param_nbdevdn)
    return self.upperband, self.middleband, self.lowerband

  def buy_condition(self):
    return crossover(self.data.Close,self.lowerband)
    
  def sell_condition(self):
    return crossover(self.upperband,self.data.Close)

  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size,stop=self.lowerband[-1])
        #self.buy(size=self.param_size,sl=self.lowerband[-1])
      self.long_pos = True
      self.short_pos = False
      
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size,stop=self.upperband[-1])
        #self.sell(size=self.param_size,sl=self.upperband[-1])
      self.long_pos = False
      self.short_pos = True
      
class Intersect(Strategy):
  strategy_list_name = ['EMA_Cross','SMA_Cross','RSI','BolingerBands','MACD_Cross','InsideBar','OutsideBar']
  strategy_list = name2strategy(strategy_list_name)
  long_pos = False
  short_pos = False
  exec(get_param_exec_str(strategy_list))
  
  def init(self):
    if 'MACD_Cross' in self.strategy_list_name:
      self.macd, self.macdsignal, self.macdhisyt = MACD_Cross.init(self)
    if 'SMA_Cross' in self.strategy_list_name:
      self.sma1 , self.sma2 = SMA_Cross.init(self)
    if 'EMA_Cross' in self.strategy_list_name:
      self.ema1 , self.ema2 = EMA_Cross.init(self)
    if 'RSI' in self.strategy_list_name:
      self.rsi = RSI.init(self)
    if 'BolingerBands' in self.strategy_list_name:
      self.upperband, self.middleband, self.lowerband = BolingerBands.init(self)

    
  def next(self):
    buy_condition = [strategy.buy_condition(self) for strategy in self.strategy_list if strategy.name in self.strategy_list_name]
    sell_condition = [strategy.sell_condition(self) for strategy in self.strategy_list if strategy.name in self.strategy_list_name]
    
    if all(buy_condition) and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    if all(sell_condition) and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True
      
class Union(Strategy):
  strategy_list_name = ['EMA_Cross','SMA_Cross','RSI','BolingerBands','MACD_Cross']
  strategy_list = name2strategy(strategy_list_name)
  long_pos = False
  short_pos = False
  exec(get_param_exec_str(strategy_list))
  
  def init(self):
    if 'MACD_Cross' in self.strategy_list_name:
      self.macd, self.macdsignal, self.macdhisyt = MACD_Cross.init(self)
    if 'SMA_Cross' in self.strategy_list_name:
      self.sma1 , self.sma2 = SMA_Cross.init(self)
    if 'EMA_Cross' in self.strategy_list_name:
      self.ema1 , self.ema2 = EMA_Cross.init(self)
    if 'RSI' in self.strategy_list_name:
      self.rsi = RSI.init(self)
    if 'BolingerBands' in self.strategy_list_name:
      self.upperband, self.middleband, self.lowerband = BolingerBands.init(self)

    
  def next(self):
    buy_condition = [strategy.buy_condition(self) for strategy in self.strategy_list if strategy.name in self.strategy_list_name]
    sell_condition = [strategy.sell_condition(self) for strategy in self.strategy_list if strategy.name in self.strategy_list_name]

    if any(buy_condition) and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
      self.long_pos = True
      self.short_pos = False
    if any(sell_condition) and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)
      self.long_pos = False
      self.short_pos = True
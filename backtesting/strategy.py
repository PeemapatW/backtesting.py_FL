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
  size = 1-1e-10
  period = 30
  directed = 0
  
  def init(self):
    close = self.data.Close
    self.sma = self.I(ta.SMA, close, self.period)
    self.dsma = self.I(dSMA, close, self.period)
    return self.sma, self.dsma
  
  def buy_condition(self):
    return crossover(self.dsma, 0)
    
  def sell_condition(self):
    return crossover(0, self.dsma)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)

class SMA_Cross(Strategy):
  name = 'SMA_Cross'
  size = 1-1e-10
  fastperiod = 10
  slowperiod = 20
  directed = 0
  
  def init(self):
    close = self.data.Close
    self.sma1 = self.I(ta.SMA, close, self.fastperiod)
    self.sma2 = self.I(ta.SMA, close, self.slowperiod)
    return self.sma1,self.sma2
  
  def buy_condition(self):
    return crossover(self.sma1, self.sma2)
    
  def sell_condition(self):
    return crossover(self.sma2, self.sma1)
  
  def next(self):
    next_(self)
    '''
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
    '''
      
class EMA_Cross(Strategy):
  name = 'EMA_Cross'
  size = 1-1e-10
  fastperiod = 10
  slowperiod = 20
  directed = 0
  
  def init(self):
    close = self.data.Close
    self.ema1 = self.I(ta.EMA, close, self.fastperiod)
    self.ema2 = self.I(ta.EMA, close, self.slowperiod)
    return self.ema1,self.ema2
  
  def buy_condition(self):
    return crossover(self.ema1, self.ema2)
    
  def sell_condition(self):
    return crossover(self.ema2, self.ema1)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      
class EMA_Cross_3Line(Strategy):
  name = 'EMA_Cross_3Line'
  size = 1-1e-10
  period1 = 10
  period2 = 20
  period3 = 30
  directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.ema1 = self.I(ta.EMA, close, self.period1)
    self.ema2 = self.I(ta.EMA, close, self.period2)
    self.ema3 = self.I(ta.EMA, close, self.period3)
    return self.ema1,self.ema2,self.ema3
  
  def buy_condition(self):
    return all([self.data.Close[-1] > ema[-1] for ema in [self.ema1,self.ema2,self.ema3]]) and any([crossover(self.data.Close, ema) for ema in [self.ema1,self.ema2,self.ema3]])
    
  def sell_condition(self):
    return all([self.data.Close[-1] < ema[-1] for ema in [self.ema1,self.ema2,self.ema3]]) and any([crossover(ema, self.data.Close) for ema in [self.ema1,self.ema2,self.ema3]])
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      self.long_pos = False
      self.short_pos = True

class EMA_Cross_4Line(Strategy):
  name = 'EMA_Cross_4Line'
  size = 1-1e-10
  period1 = 10
  period2 = 20
  period3 = 30
  period4 = 40
  directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.ema1 = self.I(ta.EMA, close, self.period1)
    self.ema2 = self.I(ta.EMA, close, self.period2)
    self.ema3 = self.I(ta.EMA, close, self.period3)
    self.ema4 = self.I(ta.EMA, close, self.period4)
    return self.ema1,self.ema2,self.ema3
  
  def buy_condition(self):
    return all([self.data.Close[-1] > ema[-1] for ema in [self.ema1,self.ema2,self.ema3,self.ema4]]) and any([crossover(self.data.Close, ema) for ema in [self.ema1,self.ema2,self.ema3,self.ema4]])
    
  def sell_condition(self):
    return all([self.data.Close[-1] < ema[-1] for ema in [self.ema1,self.ema2,self.ema3,self.ema4]]) and any([crossover(ema, self.data.Close) for ema in [self.ema1,self.ema2,self.ema3,self.ema4]])
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      self.long_pos = False
      self.short_pos = True

class WMA_Cross(Strategy):
  name = 'WMA_Cross'
  size = 1-1e-10
  fastperiod = 10
  slowperiod = 20
  directed = 0
  
  def init(self):
    close = self.data.Close
    self.wma1 = self.I(ta.WMA, close, self.fastperiod)
    self.wma2 = self.I(ta.WMA, close, self.slowperiod)
    return self.wma1,self.wma2
  
  def buy_condition(self):
    return crossover(self.wma1, self.wma2)
    
  def sell_condition(self):
    return crossover(self.wma2, self.wma1)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      
class DEMA_Cross(Strategy):
  name = 'DEMA_Cross'
  size = 1-1e-10
  fastperiod = 10
  slowperiod = 20
  directed = 0
  
  def init(self):
    close = self.data.Close
    self.dema1 = self.I(ta.DEMA, close, self.fastperiod)
    self.dema2 = self.I(ta.DEMA, close, self.slowperiod)
    return self.dema1,self.dema2
  
  def buy_condition(self):
    return crossover(self.dema1, self.dema2)
    
  def sell_condition(self):
    return crossover(self.dema2, self.dema1)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      
class TEMA_Cross(Strategy):
  name = 'TEMA_Cross'
  size = 1-1e-10
  fastperiod = 10
  slowperiod = 20
  directed = 0
  
  def init(self):
    close = self.data.Close
    self.tema1 = self.I(ta.TEMA, close, self.fastperiod)
    self.tema2 = self.I(ta.TEMA, close, self.slowperiod)
    return self.tema1,self.tema2
  
  def buy_condition(self):
    return crossover(self.tema1, self.tema2)
    
  def sell_condition(self):
    return crossover(self.tema2, self.tema1)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      
class TRIMA_Cross(Strategy):
  name = 'TRIMA_Cross'
  size = 1-1e-10
  fastperiod = 10
  slowperiod = 20
  directed = 0
  
  def init(self):
    close = self.data.Close
    self.trima1 = self.I(ta.TRIMA, close, self.fastperiod)
    self.trima2 = self.I(ta.TRIMA, close, self.slowperiod)
    return self.trima1,self.trima2
  
  def buy_condition(self):
    return crossover(self.trima1, self.trima2)
    
  def sell_condition(self):
    return crossover(self.trima2, self.trima1)
  
  def next(self):
    if self.buy_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
     
    if self.sell_condition():
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)

class RSI(Strategy):
  name = 'RSI'
  size = size = 1-1e-10
  timeperiod = 14
  overbought = 60
  oversold = 30
  delay = 1
  directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.rsi = self.I(ta.RSI, close, self.timeperiod)
    return self.rsi
  
  def buy_condition(self):
    return self.rsi[-(self.delay+1)] > self.oversold and all([self.rsi[-i] < self.oversold for i in range(1,self.delay+1)])
    #return all([self.rsi[-i] < self.oversold for i in range(1,self.delay+1)])  
    
  def sell_condition(self):
    return self.rsi[-(self.delay+1)] < self.overbought and all([self.rsi[-i] > self.overbought for i in range(1,self.delay+1)])
    #return all([self.rsi[-i] > self.overbought for i in range(1,self.delay+1)])
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      self.long_pos = False
      self.short_pos = True

class MACD_Cross(Strategy):
  name = 'MACD_Cross'
  size = 1-1e-10
  fastperiod = 12
  slowperiod = 26
  signalperiod = 9
  directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.macd, self.macdsignal, self.macdhisyt = self.I(ta.MACD,close, self.fastperiod, self.slowperiod, self.signalperiod)
    return self.macd, self.macdsignal, self.macdhisyt
  
  def buy_condition(self):
    return crossover(self.macd, self.macdsignal)
    
  def sell_condition(self):
    return crossover(self.macdsignal, self.macd)
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      self.long_pos = False
      self.short_pos = True
      
class BarUpDown(Strategy):
  name = "BarUpDown"
  size = 1-1e-10
  max_loss = 1
  directed = 0
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
      stop_loss = self.equity < self.pre_equity*(1-self.max_loss/100)
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
      if self.directed >= 0:
        self.buy(size=self.size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      self.long_pos = False
      self.short_pos = True

class ChannelBreakOut(Strategy):
  name = "ChannelBreakOut"
  size = 1-1e-10
  length = 5
  directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    pass
    
  def buy_condition(self):
    high = self.data.High
    upbound = np.max([high[-(self.length+1):-1]])
    return upbound < high[-1]
    
  def sell_condition(self):
    low = self.data.Low
    downbound = np.min([low[-(self.length+1):-1]])
    return downbound > low[-1]
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      self.long_pos = False
      self.short_pos = True
      
class InsideBar(Strategy):
  name = "InsideBar"
  size = 1-1e-10
  directed = 0
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
      if self.directed >= 0:
        self.buy(size=self.size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      self.long_pos = False
      self.short_pos = True
      
class OutsideBar(Strategy):
  name = "OutsideBar"
  size = 1-1e-10
  directed = 0
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
      if self.directed >= 0:
        self.buy(size=self.size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      self.long_pos = False
      self.short_pos = True
      
class Momentum(Strategy):
  name = "InsideBar"
  size = 1-1e-10
  length = 12
  directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.mom0 = self.I(ta.MOM,close,self.length)
    self.mom1 = self.I(ta.MOM,self.mom0, 1)
    return self.mom0, self.mom1
    
  def buy_condition(self):
    return self.mom0 > 0 and self.mom1 > 0
    
  def sell_condition(self):
    return self.mom0 < 0 and self.mom1 < 0
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
      self.long_pos = True
      self.short_pos = False
    #elif not self.buy_condition() and self.long_pos:
    #  close_opposite_dir_trade(self.trades,dir=0)
    #  self.long_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      self.long_pos = False
      self.short_pos = True
    #elif not self.sell_condition() and self.short_pos:
    #  close_opposite_dir_trade(self.trades,dir=0)
    #  self.short_pos = False
      
class ConsecutiveUpDown(Strategy):
  name = "ConsecutiveUpDown"
  size = 1-1e-10
  barsup = 3
  barsdn = 3
  directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    pass
    
  def buy_condition(self):
    close = self.data.Close
    try:
      consup = np.all(close[-(self.barsup+1):-1] < close[-self.barsup:])
    except:
      consup = False #in case of first step of iteration
    return consup
    
  def sell_condition(self):
    close = self.data.Close
    try:
      consdown = np.all(close[-(self.barsdn+1):-1] > close[-self.barsdn:])
    except:
      consdown = False
    return consdown
  
  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
      self.long_pos = True
      self.short_pos = False
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      self.long_pos = False
      self.short_pos = True
      

class BolingerBands(Strategy):
  name = 'BolingerBands'
  size = 1-1e-10
  timeperiod = 20
  nbdevup = 2
  nbdevdn = 2
  directed = 0
  long_pos = False
  short_pos = False
  
  def init(self):
    close = self.data.Close
    self.upperband, self.middleband, self.lowerband = self.I(ta.BBANDS,close, self.timeperiod, self.nbdevup, self.nbdevdn)
    return self.upperband, self.middleband, self.lowerband

  def buy_condition(self):
    return crossover(self.data.Close,self.lowerband)
    
  def sell_condition(self):
    return crossover(self.upperband,self.data.Close)

  def next(self):
    if self.buy_condition() and not self.long_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size,stop=self.lowerband[-1])
        #self.buy(size=self.size,sl=self.lowerband[-1])
      self.long_pos = True
      self.short_pos = False
      
    if self.sell_condition() and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size,stop=self.upperband[-1])
        #self.sell(size=self.size,sl=self.upperband[-1])
      self.long_pos = False
      self.short_pos = True

'''
class Intersect(Strategy):
  strategy_list_name = ['EMA_Cross','SMA_Cross','RSI','BolingerBands','MACD_Cross','InsideBar','OutsideBar']
  strategy_list = name2strategy(strategy_list_name)
  long_pos = False
  short_pos = False
  exec(get_exec_str(strategy_list))
  
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
      if self.directed >= 0:
        self.buy(size=self.size)
      self.long_pos = True
      self.short_pos = False
    if all(sell_condition) and not self.short_pos:
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)
      self.long_pos = False
      self.short_pos = True
'''
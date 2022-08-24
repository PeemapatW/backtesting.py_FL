import talib as ta
from backtesting import Backtest, Strategy
from lib import crossover, cross
from util import *

def name2strategy(name_list):
  name2strategy_dict = {'MACD_Cross':MACD_Cross,'SMA_Cross':SMA_Cross,'EMA_Cross':EMA_Cross,'DEMA_Cross':DEMA_Cross,'RSI':RSI,'BBand_UD':BBand_UD}
  return [name2strategy_dict[name] for name in name_list]
  
class HODL(Strategy):
  name = 'HODL'
  
  def init(self):
    pass
    
  def next(self):
    if len(self.data.Close)==2:
      self.buy()
      
class DCA(Strategy):
  name = 'DCA'
  param_day = 1
  
  def init(self):
    pass
    
  def next(self):
    day = self.data.index[-1].day
    if day == self.param_day:
      self.buy(size=0.1,tp=10000000000000000000)

class SMA_Cross(Strategy):
  name = 'SMA_Cross'
  param_fastperiod = 10
  param_slowperiod = 20
  
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
      self.buy()
    elif self.sell_condition():
      self.sell()
      
class EMA_Cross(Strategy):
  name = 'EMA_Cross'
  param_fastperiod = 10
  param_slowperiod = 20
  
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
      self.buy()
    elif self.sell_condition():
      self.sell()
      
class WMA_Cross(Strategy):
  name = 'WMA_Cross'
  param_fastperiod = 10
  param_slowperiod = 20
  
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
      self.buy()
    elif self.sell_condition():
      self.sell()
      
class DEMA_Cross(Strategy):
  name = 'DEMA_Cross'
  param_fastperiod = 10
  param_slowperiod = 20
  
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
      self.buy()
    elif self.sell_condition():
      self.sell()
      
class TEMA_Cross(Strategy):
  name = 'TEMA_Cross'
  param_fastperiod = 10
  param_slowperiod = 20
  
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
      self.buy()
    elif self.sell_condition():
      self.sell()
      
class TRIMA_Cross(Strategy):
  name = 'TRIMA_Cross'
  param_fastperiod = 10
  param_slowperiod = 20
  
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
      self.buy()
    elif self.sell_condition():
      self.sell()

class RSI(Strategy):
  name = 'RSI'
  param_timeperiod = 14
  param_overbought = 60
  param_oversold = 30
  param_delay = 1
  
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
    if self.buy_condition():
      self.buy()
    elif self.sell_condition():
      self.sell()

class MACD_Cross(Strategy):
  name = 'MACD_Cross'
  param_fastperiod = 12
  param_slowperiod = 29
  param_signalperiod = 9
  
  def init(self):
    close = self.data.Close
    self.macd, self.macdsignal, self.macdhisyt = self.I(ta.MACD,close, self.param_fastperiod, self.param_slowperiod, self.param_signalperiod)
    return self.macd, self.macdsignal, self.macdhisyt
  
  def buy_condition(self):
    return crossover(self.macd, self.macdsignal)
    
  def sell_condition(self):
    return crossover(self.macdsignal, self.macd)
  
  def next(self):
    if self.buy_condition():
      self.buy()
    elif self.sell_condition():
      self.sell()
      
class BBand_UD(Strategy):
  name = 'BBand_UD'
  param_timeperiod = 20
  param_nbdevup = 2
  param_nbdevdn = 2
  
  def init(self):
    close = self.data.Close
    self.upperband, self.middleband, self.lowerband = self.I(ta.BBANDS,close, self.param_timeperiod, self.param_nbdevup, self.param_nbdevdn)
    return self.upperband, self.middleband, self.lowerband
  
  def buy_condition(self):
    return self.data.Close[-1] < self.lowerband[-1] and self.data.Close[-2] > self.lowerband[-2]
    
  def sell_condition(self):
    return self.upperband[-1] < self.data.Close[-1] and self.upperband[-2] > self.data.Close[-2]
  
  def next(self):
    if self.buy_condition():
      self.buy()
    elif self.sell_condition():
      self.sell()
      
class Intersect_Strategy(Strategy):
  strategy_list_name = ['MACD_Cross','SMA_Cross','EMA_Cross','DEMA_Cross','RSI','BBand_UD']
  strategy_list = name2strategy(strategy_list_name)
  exec(get_param_exec_str(strategy_list))
  
  def init(self):
    if 'MACD_Cross' in self.strategy_list_name:
      self.macd, self.macdsignal, self.macdhisyt = MACD_Cross.init(self)
    if 'SMA_Cross' in self.strategy_list_name:
      self.sma1 , self.sma2 = SMA_Cross.init(self)
    if 'RSI' in self.strategy_list_name:
      self.rsi = RSI.init(self)
    if 'BBand_UD' in self.strategy_list_name:
      self.upperband, self.middleband, self.lowerband = BBand_UD.init(self)

    
  def next(self):
    buy = True
    sell = True
    if 'MACD_Cross' in self.strategy_list_name:
      buy = buy and MACD_Cross.buy_condition(self)
      sell = sell and MACD_Cross.sell_condition(self)
    if 'SMA_Cross' in self.strategy_list_name:
      buy = buy and SMA_Cross.buy_condition(self)
      sell = sell and SMA_Cross.sell_condition(self)
    if 'RSI' in self.strategy_list_name:
      buy = buy and RSI.buy_condition(self)
      sell = sell and RSI.sell_condition(self)
    if 'BBand_UD' in self.strategy_list_name:
      buy = buy and BBand_UD.buy_condition(self)
      sell = sell and BBand_UD.sell_condition(self)
      
    if buy:
      self.buy()
    elif sell:
      self.sell()
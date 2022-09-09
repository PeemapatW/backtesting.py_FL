import talib as ta
from backtesting import Backtest, Strategy
from lib import crossover, cross
from util import *
from _util import _Indicator
from strategy import *
import numpy as np
import copy

def all_open_any_close(case_list,type):
  if type == 'open':
    return all(case_list)
  elif type == 'close':
    return any(case_list)
  else:
    raise ValueError('type must be \'open\' or \'close')

def all_open_all_close(case_list,type):
  return all(case_list)

def any_open_any_close(case_list,type):
    return any(case_list)

class CombiningStrategy(Strategy):
  strategy_list = [(SMA_Cross,dict(fastperiod=25,slowperiod=50))]
  condition = 'All'
  directed = 0
  size = 1-1e-10
 
  def init(self):
    for strategy_, params in self.strategy_list:
      setattr(self,strategy_.__name__,eval(strategy_.__name__+'(self._broker, self._data, params=params)'))
      strategy = getattr(self,strategy_.__name__)
      ind = strategy.init()
      indicator_attrs = {attr: indicator for attr, indicator in strategy.__dict__.items() if isinstance(indicator, _Indicator)}.items()
      setattr(strategy,'indicator_attrs',indicator_attrs)
      # Assign indicator for make them enabled to plot with bt.plot()
      for attr, indicator in indicator_attrs:
        setattr(self, attr, self.I(lambda x:x,indicator,name=indicator.name))
      
  def next(self):
    buy_condition = []
    sell_condition = []
    for strategy in list(zip(*self.strategy_list))[0]:
      buy_condition.append(getattr(self,strategy.name).buy_condition())
      sell_condition.append(getattr(self,strategy.name).sell_condition())
      
    #print(self.condition)
    
    if self.condition.casefold() == 'all':
      func = all_open_all_close
    elif self.condition.casefold() == 'any':
      func = any_open_any_close
    elif self.condition.casefold() == 'all-any':
      func = all_open_any_close
    else:
      raise ValueError("Currently support only \"all\" or \"any\" condition")
    
    if all([t.size < 0 for t in self.trades]): # Current set of trades is short or not hold any position
      if func(buy_condition,'close'):# If condition met for close current short position
        [t.close() for t in self.trades] # Close all of hold position
      if func(buy_condition,'open') and self.directed >= 0: # If condition met for open long position
        self.buy(size=self.size) # Open long
        
    if all([t.size > 0 for t in self.trades]):  # Current set of trades is long or not hold any position
      if func(sell_condition,'close'): # If condition met for close current long position
        [t.close() for t in self.trades] # Close all of hold position
      if func(sell_condition,'open') and self.directed <= 0: # If condition met for open short position
        self.sell(size=self.size) # Open short

'''
    if func(buy_condition):
      if len(self.trades) > 0:
        if all([t.size < 0 for t in self.trades]):
          [t.close() for t in self.trades]
          if self.directed >= 0:
            self.buy(size=self.size)
      else:
         if self.directed >= 0:
          self.buy(size=self.size)

     
    if func(sell_condition):
      if len(self.trades) > 0:
        if all([t.size > 0 for t in self.trades]):
          [t.close() for t in self.trades]
          if self.directed <= 0:
            self.sell(size=self.size)
      else:
        if self.directed <= 0:
            self.sell(size=self.size)
'''
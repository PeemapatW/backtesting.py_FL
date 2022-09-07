import talib as ta
from backtesting import Backtest, Strategy
from lib import crossover, cross
from util import *
from _util import _Indicator
from strategy import *
import numpy as np
import copy

def Ind(x):
  return x

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
    
    if self.condition.casefold() == 'all':
      func = all
    elif self.condition.casefold() == 'any':
      func = any
    else:
      raise ValueError("Currently support only \"all\" or \"any\" condition")
      
    if func(buy_condition):
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed >= 0:
        self.buy(size=self.size)
     
    if func(sell_condition):
      close_opposite_dir_trade(self.trades,dir=0)
      if self.directed <= 0:
        self.sell(size=self.size)


'''

class CombiningStrategy(Strategy):
  strategy_list = []
  condition = 'All'
  param_directed = 0
  param_size = 1-1e-10
  
  def init(self, **kwargs):
    for strategy in self.strategy_list:
      exec('self.'+strategy.name+'='+strategy.name+'(self._broker, self._data, kwargs)')
      ind = eval('self.'+strategy.name+'.init()')
      # Assign indicator for make them enabled to plot with bt.plot()
      for i in range(len(ind)):
        exec('self.ind'+str(i)+' = self.I(Ind, ind[i])')
      
  def next(self):
    buy_condition = []
    sell_condition = []
    for strategy in self.strategy_list:
      #buy_condition.append(eval('self.'+strategy.name+'.buy_condition()'))
      #sell_condition.append(eval('self.'+strategy.name+'.sell_condition()'))
      buy_condition.append(strategy.buy_condition(self))
      sell_condition.append(strategy.sell_condition(self))
      #buy_condition.append(eval(strategy.name+'.buy_condition(self.'+strategy.name+ ')'))
      #sell_condition.append(eval(strategy.name+'.sell_condition(self.'+strategy.name+ ')'))
    
    
    if all(buy_condition):
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed >= 0:
        self.buy(size=self.param_size)
     
    if all(sell_condition):
      close_opposite_dir_trade(self.trades,dir=0)
      if self.param_directed <= 0:
        self.sell(size=self.param_size)

'''
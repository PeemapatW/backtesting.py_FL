from datetime import datetime
from time import mktime
import inspect
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from yahoo_fin.stock_info import get_data


def get_from_glassnode_api(asset,metrics,resolution='24h',start=0,end=0,API_KEY='2DTcBg9x0YgVPwieR9fybZAlGoA'):
  if start != 0:
    start = int(time.mktime(datetime.datetime.strptime(start, '%d/%m/%y %H:%M:%S').timetuple()))
  if end != 0:
    end = int(time.mktime(datetime.datetime.strptime(end, '%d/%m/%y %H:%M:%S').timetuple()))
  
  params = {'a': asset, 's':start, 'u':end, 'i':resolution, 'api_key': API_KEY}
  api_url_dict = {'price':'https://api.glassnode.com/v1/metrics/market/price_usd_close',
             'active':'https://api.glassnode.com/v1/metrics/addresses/active_count',
             'balance_exchange':'https://api.glassnode.com/v1/metrics/distribution/balance_exchanges',
             'exchange_deposits':'https://api.glassnode.com/v1/metrics/transactions/transfers_to_exchanges_count',
             'exchange_withdrawals':'https://api.glassnode.com/v1/metrics/transactions/transfers_from_exchanges_count',
             'transfers_volume_total':'https://api.glassnode.com/v1/metrics/transactions/transfers_volume_sum'}
  get_df = {}
  for metric in metrics:
    try: 
      read_data = pd.read_json(requests.get(api_url_dict[metric],params=params).text, convert_dates=['t']).set_index('t')
    except:
      read_data = pd.DataFrame([np.nan]*len(get_df[list(get_df.keys())[0]]),index=get_df[list(get_df.keys())[0]].index)
    get_df[metric] = read_data
  return get_df

def param_dict_to_eval_str(param_dict):
  hyper_param = ""
  for key in param_dict.keys(): 
    hyper_param = hyper_param + key + '=' + str(param_dict[key]) + ','
  return hyper_param[:-1]

def opt_param_dict_to_eval_str(param_dict):
  hyper_param = ""
  for key in param_dict.keys(): 
    hyper_param = hyper_param + key + '=' + str(param_dict[key]) + ','
  if 'param_fastperiod' in param_dict.keys() and 'param_slowperiod' in param_dict.keys():
    hyper_param += 'constraint=lambda p: p.param_fastperiod < p.param_slowperiod,'
  return hyper_param[:-1]

def Test_Strategy(ticker,strategy,param={},start_date="01/01/18",end_date='',test_interval=0,resolution='1d',plot=True,optimize=False,exclusive_orders=False):
  if not (isinstance(start_date,str) or isinstance(start_date,datetime)) and not (isinstance(end_date,str) or isinstance(end_date,datetime)):
    raise ValueError("input date must be in str dd/mm/yy or in datetime format")
  if end_date == '' and test_interval == 0:
    raise ValueError("must be atleast input end_date or test_interval")
  if isinstance(start_date,datetime):
    start_date = start_date.strftime('%m/%d/%y')
  if isinstance(end_date,datetime):
    end_date = end_date.strftime('%m/%d/%y')
  if test_interval > 0:
    resolustion_timestamp_dict = {'1d':86400}
    end_date = datetime.fromtimestamp(mktime(datetime.strptime(start_date, '%m/%d/%y').timetuple()) + test_interval*resolustion_timestamp_dict[resolution]).strftime('%m/%d/%y')
  try:
    data = get_data(ticker=ticker,start_date=start_date,end_date=end_date,interval=resolution).dropna()
    data.columns = [col_name.capitalize() for col_name in data.columns]
    data = data[data.Close!=0]
    bt = Backtest(data, strategy,cash=1000000, commission=.002,exclusive_orders=exclusive_orders)
    if not optimize:
      output = eval("bt.run("+param_dict_to_eval_str(param)+")")
    else:
      output = eval("bt.optimize("+opt_param_dict_to_eval_str(param)+', return_heatmap=True)[0]')
    if plot : bt.plot()
  except ValueError:
    print("input ticker is not valid or there are no data in the selected interval")
    bt = np.nan
    output = np.nan
  
  return bt,output

def get_param_exec_str(strategy_list):
  exec_str = ""
  for strategy in strategy_list:
    all_attr = inspect.getmembers(strategy, lambda a:not(inspect.isroutine(a)))
    param_attr = [all_attr[idx] for idx in range(len(all_attr)) if 'param_' in all_attr[idx][0]]
    for param in param_attr:
      exec_str = exec_str + param[0] + '=' + str(param[1]) + ";"
  return exec_str[:-1]
  
  

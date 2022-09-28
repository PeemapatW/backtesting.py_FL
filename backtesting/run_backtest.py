from backtesting import Backtest, Strategy
from strategy import *
from util import *
from c_strategy import *
import argparse
import json

def main(opt):
  f = open(opt.input)
  input_data = json.load(f)
  result = {}
  for i, input in input_data.items():
    print(input)
    data = get_ohlcv_glassnode_api(input['ticker'],resolution=input['resolution'],start=input['start_date'],end=input['end_date'],API_KEY='2DTcBg9x0YgVPwieR9fybZAlGoA')
    bt = Backtest(data, CombiningStrategy ,cash=input['cash'],commission=input['commission'])
    bt.run(strategy_list = eval(input['strategy_list']),condition = input['condition'], size=input['size'],directed=input['directed'],
          stop_loss = input['stop_loss'], take_profit = input['take_profit'])
    key_results = bt._key_results
    result[i] = bt._key_results
    indicators = bt._results._strategy._indicators
    indicator_df = pd.concat([ind.df for ind in indicators], join='inner',axis=1)
    trade_tables_df = bt._results._trades
    key_results['Indicators'] = indicator_df
    key_results['Trade Tables'] = trade_tables_df
    result[i] = key_results
    bt.plot(filename=str(i)+'_output')
  result_df = pd.DataFrame(result)
  result_df.to_json(r'output.json')

def parse_opt(known=False):
  parser = argparse.ArgumentParser()
  print(parser)
  parser.add_argument('--input', type=str, default='example_input.json',help='path to json')
  return parser.parse_known_args()[0] if known else parser.parse_args()

if __name__ == "__main__":
  opt = parse_opt()
  main(opt)
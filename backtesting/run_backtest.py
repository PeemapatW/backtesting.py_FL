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
    result[i] = bt._results
    bt.plot(filename=str(i)+'_output')
    print(result[i])

def parse_opt(known=False):
  parser = argparse.ArgumentParser()
  print(parser)
  parser.add_argument('--input', type=str, default='example_input.json',help='path to json')
  return parser.parse_known_args()[0] if known else parser.parse_args()

if __name__ == "__main__":
  opt = parse_opt()
  main(opt)
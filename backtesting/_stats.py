from typing import List, TYPE_CHECKING, Union

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from datetime import timedelta

from _util import _data_period

if TYPE_CHECKING:
    from .backtesting import Strategy, Trade


def compute_drawdown_duration_peaks(dd: pd.Series):
    iloc = np.unique(np.r_[(dd == 0).values.nonzero()[0], len(dd) - 1])
    iloc = pd.Series(iloc, index=dd.index[iloc])
    df = iloc.to_frame('iloc').assign(prev=iloc.shift())
    df = df[df['iloc'] > df['prev'] + 1].astype(int)

    # If no drawdown since no trade, avoid below for pandas sake and return nan series
    if not len(df):
        return (dd.replace(0, np.nan),) * 2

    df['duration'] = df['iloc'].map(dd.index.__getitem__) - df['prev'].map(dd.index.__getitem__)
    df['peak_dd'] = df.apply(lambda row: dd.iloc[row['prev']:row['iloc'] + 1].max(), axis=1)
    df = df.reindex(dd.index)
    return df['duration'], df['peak_dd']


def geometric_mean(returns: pd.Series) -> float:
    returns = returns.fillna(0) + 1
    if np.any(returns <= 0):
        return 0
    return np.exp(np.log(returns).sum() / (len(returns) or np.nan)) - 1


def compute_stats(
        trades: Union[List['Trade'], pd.DataFrame],
        equity: np.ndarray,
        ohlc_data: pd.DataFrame,
        strategy_instance: 'Strategy',
        risk_free_rate: float = 0,
        alpha : float = 0.05,
) -> pd.Series:
    assert -1 < risk_free_rate < 1
    
    index = ohlc_data.index
    dd = 1 - equity / np.maximum.accumulate(equity)
    dd_equity = np.maximum.accumulate(equity) - equity
    dd_dur, dd_peaks = compute_drawdown_duration_peaks(pd.Series(dd, index=index))
    dd_dur_equity, dd_peaks_equity = compute_drawdown_duration_peaks(pd.Series(dd_equity, index=index))

    equity_df = pd.DataFrame({
        'Equity': equity,
        'DrawdownPct': dd,
        'DrawdownDuration': dd_dur},
        index=index)

    if isinstance(trades, pd.DataFrame):
        trades_df = trades
    else:
        # Came straight from Backtest.run()
        trades_df = pd.DataFrame({
            'Size': [t.size for t in trades],
            'EntryBar': [t.entry_bar for t in trades],
            'ExitBar': [t.exit_bar for t in trades],
            'EntryPrice': [t.entry_price for t in trades],
            'ExitPrice': [t.exit_price for t in trades],
            'PnL': [t.pl for t in trades],
            'ReturnPct': [t.pl_pct for t in trades],
            'EntryTime': [t.entry_time for t in trades],
            'ExitTime': [t.exit_time for t in trades],
        })
        trades_df['Duration'] = trades_df['ExitTime'] - trades_df['EntryTime']
    del trades
    


    pl = trades_df['PnL']
    returns = trades_df['ReturnPct']
    durations = trades_df['Duration']

    def _round_timedelta(value, _period=_data_period(index)):
        if not isinstance(value, pd.Timedelta):
            return value
        resolution = getattr(_period, 'resolution_string', None) or _period.resolution
        return value.ceil(resolution)

    s = pd.Series(dtype=object)
    s.loc['Start'] = index[0]
    s.loc['End'] = index[-1]
    s.loc['Duration'] = s.End - s.Start

    have_position = np.repeat(0, len(index))
    for t in trades_df.itertuples(index=False):
        have_position[t.EntryBar:t.ExitBar + 1] = 1

    s.loc['Exposure Time [%]'] = have_position.mean() * 100  # In "n bars" time, not index time
    s.loc['Equity Final [$]'] = equity[-1]
    s.loc['Equity Peak [$]'] = equity.max()
    s.loc['Return [%]'] = (equity[-1] - equity[0]) / equity[0] * 100
    s.loc['Return'] = (equity[-1] - equity[0])
    s.loc['Log Return'] = np.nan if equity[-1] == 0 else np.log(equity[-1]/equity[0])
    c = ohlc_data.Close.values
    s.loc['Buy & Hold Return [%]'] = (c[-1] - c[0]) / c[0] * 100  # long-only return
    s.loc['Buy & Hold Log Return'] = np.log(c[-1]/c[0])
    #o = ohlc_data.Open.values
    #s.loc['Buy & Hold Return [%] with open'] = (c[-1] - o[0]) / o[0] * 100  # long-only return

    monthly_close = ohlc_data[ohlc_data.index.day == 1].Close.values
    #initial_equity = equity[0]
    #dcapm = initial_equity/len(monthly_close)
    ### NEED TO IMPROVE FOR OTHER ASSET THAT CANNOT TRADE EVERYDAY ####
    s.loc['DCA Return [%]'] = (np.sum([1/close for close in monthly_close])*c[-1]-len(monthly_close))/len(monthly_close)*100  # dca return

    gmean_day_return: float = 0
    day_returns = np.array(np.nan)
    annual_trading_days = np.nan
    if isinstance(index, pd.DatetimeIndex):
        day_returns = equity_df['Equity'].resample('D').last().dropna().pct_change()
        gmean_day_return = geometric_mean(day_returns)
        annual_trading_days = float(
            365 if index.dayofweek.to_series().between(5, 6).mean() > 2/7 * .6 else
            252)

    # Annualized return and risk metrics are computed based on the (mostly correct)
    # assumption that the returns are compounded. See: https://dx.doi.org/10.2139/ssrn.3054517
    # Our annualized return matches `empyrical.annual_return(day_returns)` whereas
    # our risk doesn't; they use the simpler approach below.
    annualized_return = (1 + gmean_day_return)**annual_trading_days - 1
    s.loc['Return (Ann.) [%]'] = annualized_return * 100
    # Separate equation to 3 part for avoiding overflow
    #s.loc['Volatility (Ann.) [%]'] = np.sqrt((day_returns.var(ddof=int(bool(day_returns.shape))) + (1 + gmean_day_return)**2)**annual_trading_days - (1 + gmean_day_return)**(2*annual_trading_days)) * 100  # noqa: E501
    vol_a = day_returns.var(ddof=int(bool(day_returns.shape)))
    vol_b = ((1 + gmean_day_return)**2)**annual_trading_days
    vol_c = (1 + gmean_day_return)**(2*annual_trading_days)
    s.loc['Volatility (Ann.) [%]'] = np.sqrt(vol_a+vol_b+vol_c) * 100
    
    # s.loc['Return (Ann.) [%]'] = gmean_day_return * annual_trading_days * 100
    # s.loc['Risk (Ann.) [%]'] = day_returns.std(ddof=1) * np.sqrt(annual_trading_days) * 100

    # Our Sharpe mismatches `empyrical.sharpe_ratio()` because they use arithmetic mean return
    # and simple standard deviation
    s.loc['Sharpe Ratio'] = np.clip((s.loc['Return (Ann.) [%]'] - risk_free_rate) / (s.loc['Volatility (Ann.) [%]'] or np.nan), 0, np.inf)  # noqa: E501
    # Our Sortino mismatches `empyrical.sortino_ratio()` because they use arithmetic mean return
    s.loc['Sortino Ratio'] = np.clip((annualized_return - risk_free_rate) / (np.sqrt(np.mean(day_returns.clip(-np.inf, 0)**2)) * np.sqrt(annual_trading_days)), 0, np.inf)  # noqa: E501
    max_dd = -np.nan_to_num(dd.max())
    max_dd_equity = -dd_equity[dd.argmax()]
    s.loc['Calmar Ratio'] = np.clip(annualized_return / (-max_dd or np.nan), 0, np.inf)
    s.loc['Max. Drawdown [%]'] = max_dd * 100
    s.loc['Max. Drawdown'] = max_dd_equity
    s.loc['Avg. Drawdown [%]'] = -dd_peaks.mean() * 100
    s.loc['Avg. Drawdown'] = -dd_peaks_equity.mean()
    s.loc['Max. Drawdown Duration'] = _round_timedelta(dd_dur.max())  
    s.loc['Avg. Drawdown Duration'] = _round_timedelta(dd_dur.mean())

    size = trades_df['Size']
    s.loc['# Trades'] = n_trades = len(trades_df)
    s.loc['# Short'] = n_short = (size < 0).sum()
    s.loc['# Long'] = n_long = (size > 0).sum()
    s.loc['# Win'] = n_win = (pl > 0).sum()
    s.loc['# Loss'] = n_loss = n_trades - n_win
    s.loc['Short %'] = np.nan if not n_trades else n_short/n_trades*100
    s.loc['Long %'] = np.nan if not n_trades else n_long/n_trades*100
    
    s.loc['Win Rate [%]'] = np.nan if not n_trades else (pl > 0).sum() / n_trades * 100  # noqa: E501
    s.loc['p-value for Win Rate > 50%'] = np.nan if not n_trades else stats.binomtest((pl > 0).sum(),n_trades,p=0.5,alternative='greater').pvalue
    s.loc['Win Rate > 50%'] = np.nan if not n_trades else s.loc['p-value for Win Rate > 50%'] < alpha

    s.loc['Best Trade P&L'] = pl.max()
    s.loc['Worst Trade P&L'] = pl.min()
    s.loc['Avg. Trade (Geometric) P&L'] = geometric_mean(pl)
    s.loc['Avg. Trade (Arithmetic) P&L'] = np.mean(pl)
    s.loc['Avg. Profit (Geometric) P&L'] = geometric_mean(pl[pl > 0]) * 100
    s.loc['Avg. Profit (Arithmetic) P&L'] = np.mean(pl[pl > 0]) * 100
    s.loc['Avg. Loss (Geometric) P&L'] = -geometric_mean(-pl[pl <= 0]) * 100
    s.loc['Avg. Loss (Arithmetic) P&L'] = np.mean(pl[pl <= 0]) * 100


    if len(pl) > 1:
      t_pnl, p_pnl = stats.ttest_1samp(pl, 0,alternative='greater')    
    else:
      t_pnl, p_pnl = np.nan, np.nan
    s.loc['t_score for Avg. Trade P&L > 0'] = t_pnl
    s.loc['p-value for Avg. Trade P&L > 0'] = p_pnl
    s.loc['Avg. Trade P&L > 0'] = s.loc['p-value for Avg. Trade P&L > 0'] < alpha

    resolution = index[1]-index[0]
    bar_per_month = int(timedelta(days=30)/resolution)

    cut_c = c[np.arange(0,len(c),bar_per_month)]
    cut_e = equity[np.arange(0,len(c),bar_per_month)]
    strategy_return = np.array([(cut_e[i]-cut_e[i-1])/cut_e[i-1]*100 for i in range(1,len(cut_e))])
    market_return = np.array([(cut_c[i]-cut_c[i-1])/cut_c[i-1]*100 for i in range(1,len(cut_c))])
    
    ## Capital Assets Pricing Model (CAPM)
    ## Alpha = Return - risk_free_rate - beta(Market_return - risk_free_rate)
    Y = strategy_return - risk_free_rate
    X = market_return - risk_free_rate
    X = sm.add_constant(X)
    reg = sm.OLS(Y,X)
    reg_result = reg.fit()
    alpha_hat, beta_hat = reg_result.params
    conf_alpha_hat, conf_beta_hat = reg_result.conf_int()
    t_alpha_hat, t_beta_hat = reg_result.tvalues
    s.loc['Alpha hat'] = alpha_hat
    s.loc['Confidence Interval of Alpha hat'] = conf_alpha_hat
    s.loc['Alpha hat > 0'] = t_alpha_hat > stats.t(len(X)-1).ppf(1-alpha)
     
    s.loc['Best Trade [%]'] = returns.max() * 100
    s.loc['Worst Trade [%]'] = returns.min() * 100
    mean_return = geometric_mean(returns)
    s.loc['Avg. Trade (Geometric) [%]'] = mean_return * 100
    s.loc['Avg. Trade (Arithmetic) [%]'] = np.mean(returns) * 100

    s.loc['Avg. Profit (Geometric) [%]'] = geometric_mean(returns[returns >= 0]) * 100
    s.loc['Avg. Profit (Arithmetic) [%]'] = np.mean(returns[returns >= 0]) * 100
    s.loc['Avg. Loss (Geometric) [%]'] = -geometric_mean(-returns[returns < 0]) * 100
    s.loc['Avg. Loss (Arithmetic) [%]'] = np.mean(returns[returns < 0]) * 100

    if np.abs(s.loc['Avg. Profit (Arithmetic) [%]']) >= np.abs(s.loc['Avg. Loss (Arithmetic) [%]']):
      risk = 1
      reward = np.abs(s.loc['Avg. Profit (Arithmetic) [%]'] / s.loc['Avg. Loss (Arithmetic) [%]'])
      reward = np.round(reward,1)
      if reward.is_integer():
        reward = int(reward)
    else:
      risk = np.abs(s.loc['Avg. Loss (Arithmetic) [%]'] / s.loc['Avg. Profit (Arithmetic) [%]'])
      risk = np.round(risk,1)
      if risk.is_integer():
        risk = int(risk)
      reward = 1
    s.loc['Risk : Reward'] = str(risk) + ':' + str(reward)

    s.loc['Max. Trade Duration'] = _round_timedelta(durations.max())
    s.loc['Avg. Trade Duration'] = _round_timedelta(durations.mean())
    s.loc['Profit Factor'] = returns[returns > 0].sum() / (abs(returns[returns < 0].sum()) or np.nan)  # noqa: E501
    s.loc['Expectancy [%]'] = returns.mean() * 100
    s.loc['SQN'] = np.sqrt(n_trades) * pl.mean() / (pl.std() or np.nan)

    s.loc['_strategy'] = strategy_instance
    s.loc['_equity_curve'] = equity_df
    s.loc['_trades'] = trades_df

    s = _Stats(s)
    return s


class _Stats(pd.Series):
    def __repr__(self):
        # Prevent expansion due to _equity and _trades dfs
        with pd.option_context('max_colwidth', 20):
            return super().__repr__()

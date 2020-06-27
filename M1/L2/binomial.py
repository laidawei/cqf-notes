
# -*- coding: utf-8 -*-

# @date   : 2020-06-26
# @author : Guo Peng
# @brief  : option pricing by binomial tree

import math

def _print(lst):
    sep = ' ' * 4
    fmt = '{:6.2f}'
    prefix = ' ' * 5

    row_number = len(lst)
    for row_index, row in enumerate(lst) :
        print(prefix * (row_number - row_index), end='')
        for col_index, col in enumerate(row) :
            print(fmt.format(col), end=sep)
        print()

def _payoff(S, K, *args, **kwargs) :
    '''option payoff

    Args :
        S [float] asset spot price
        K [float] option strike price

    Return :
        [float] option payoff
    '''
    return 0 if S < K else S - K

def _pricing(S, K, u, d, p, df, N, payoff=_payoff, early=False) :
    '''option pricing (uni discount factor)

    Args :
        S  [float] asset spot price
        K  [float] option strike price
        u  [float] up multiplier
        d  [float] down multiplier
        p  [float] risk-netural probability
        df [float] discount factor
        N  [int]   step number
        payoff [function] payoff(S, K, *args, **kwargs)
        early [bool] early exercise

    Return :
        [dict] price of option
    '''
    # 计算底层资产价格二叉树 ：从第一步往后推导
    asset_tree = [[S, ],]
    for n in range(1, N + 1) :
        lst = []
        for i in range(0, n) :
            # 价格=前一步对应位置的价格*上涨因子
            lst.append(asset_tree[n-1][i] * u)
        # 最下面一个节点的价格=前一步最下方价格*下跌因子
        lst.append(asset_tree[n-1][-1] * d)
        asset_tree.append(lst)

    # 计算期权payoff二叉树：从最后一步倒推
    option_tree = [[] for _ in range(len(asset_tree)) ]
    # 计算终点的期权payoff
    last_step = asset_tree[-1]
    for asset_price in last_step :
        option_tree[-1].append(payoff(asset_price, K))

    # 倒推
    for n in range(len(option_tree) - 1, 0, -1) :
        next_step = option_tree[n]
        for i in range(len(next_step) - 1) :
            # 上涨和下跌两个分支的期望*折现因子
            v = (p * next_step[i] + (1 - p) * next_step[i + 1]) * df
            if early :
                tmp = payoff(asset_tree[n-1][i], K)
                v = v if v > tmp else tmp # 如果期权payoff比价格高，选择提前行权获取更高收益
            option_tree[n - 1].append(v)

    return {
        'result' : option_tree[0][0],
        'inter' : { 'asset' : asset_tree, 'option' : option_tree, },
        'param' : { 'S' : S, 'K' : K, 'u' : u, 'd' : d, 'p' : p, 'df' : df, },
    }

def _pricing_model1(S, K, sigma, drift, T, N, payoff=_payoff, early=False) :
    '''option pricing model 1

    Args :
        S     [float] asset spot price
        K     [float] option strike price
        sigma [float] σ, volatility of asset price
        drift [float] μ, risk-free rate
        T     [float] expiry time in year
        N     [int]   step number

    Return :
        [dict] price of option
    '''
    # 计算参数
    time_step = T / N # 步长
    df = math.exp(-drift * time_step) # 折现因子
    temp1 = sigma * math.sqrt(time_step)
    u = 1 + temp1 # 上涨因子
    d = 1 - temp1 # 下跌因子
    p = 0.5 + 0.5 * drift * math.sqrt(time_step) / sigma # 上涨概率（风险中性概率）

    r = _pricing(S, K, u, d, p, df, N, payoff, early)

    return {
        'result' : r['result'],
        'inter' : {
            'asset' : r['inter']['asset'], 'option' : r['inter']['option'],
            'time_step' : time_step, 'u' : u, 'd' : d, 'p' : p, 'df' : df,
        },
        'param' : {'S' : S, 'K' : K, 'sigma' : sigma, 'drift' : drift, 'T' : T, 'N' : N, },
    }

def _pricing_model2(S, K, sigma, drift, T, N, payoff=_payoff, early=False) :
    '''option pricing model 2

    Args :
        S     [float] asset spot price
        K     [float] option strike price
        sigma [float] σ, volatility of asset price
        drift [float] μ, risk-free rate
        T     [float] expiry time in year
        N     [int]   step number

    Return :
        [dict] price of option
    '''
    # 计算参数
    time_step = T / N # 步长
    df = math.exp(-drift * time_step) # 折现因子
    temp1 = math.exp((drift + math.pow(sigma, 2)) * time_step)
    temp2 = 0.5 * (df + temp1)
    u = temp2 + math.sqrt(math.pow(temp2, 2) - 1) # 上涨因子
    d = 1 / u # 下跌因子
    p = (math.exp(drift * time_step) - d) / (u - d) # 上涨概率（风险中性概率）

    r = _pricing(S, K, u, d, p, df, N, payoff, early)

    return {
        'result' : r['result'],
        'inter' : {
            'asset' : r['inter']['asset'], 'option' : r['inter']['option'],
            'time_step' : time_step, 'u' : u, 'd' : d, 'p' : p, 'df' : df,
        },
        'param' : {'S' : S, 'K' : K, 'sigma' : sigma, 'drift' : drift, 'T' : T, 'N' : N, },
    }

if __name__ == '__main__':
    S = 100.
    K = 100.
    sigma = 0.2
    drift = 0.05
    T = 1
    N = 4

    result = _pricing_model2(S, K, sigma, drift, T, N)
    _print(result['inter']['asset'])
    _print(result['inter']['option'])

    print(result)

    label_common = 'S={}, K={}, μ={}, T={}'.format(S, K, drift, T)

    N_list = range(1, 253, 1)
    step_result_list = [ _pricing_model2(S, K, sigma, drift, T, N)['result'] for N in N_list ]

    import numpy as np
    N = 4
    sigma_list = np.arange(0.01, 1.0, 0.01)
    sigma_result_list = [  _pricing_model2(S, K, sigma, drift, T, N)['result'] for sigma in sigma_list ]

    import matplotlib.pyplot as plt

    def _plot(ax, x, y, label, fontsize=20) :
        ax.scatter(x, y, label=label)
        ax.legend(fontsize=fontsize)
        [label.set_fontsize(fontsize) for label in ax.get_xticklabels() + ax.get_yticklabels()]
        ax.grid()

    label = 'step number(σ={}, {})'.format(sigma, label_common)
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(24, 16))
    _plot(axes[0], N_list, step_result_list, label)
    _plot(axes[1], N_list[::2], step_result_list[::2], 'odd  ' + label)
    _plot(axes[2], N_list[1::2], step_result_list[1::2], 'even ' + label)
    fig.savefig('./bt_ex.jpg')

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(16, 16))
    _plot(axes[0], N_list[1::2], step_result_list[1::2], 'even ' + label)
    label = 'σ(step number={}, {})'.format(N, label_common)
    _plot(axes[1], sigma_list, sigma_result_list, label)
    fig.savefig('./bt.jpg')

    plt.show()

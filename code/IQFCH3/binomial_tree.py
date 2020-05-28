
# -*- coding: utf-8 -*-

# @date   : 2020-05-26
# @author : Guo Peng
# @brief  : 期权定价

import math

def option_price_by_binomial_tree(
    asset_spot_price,
    volatility,
    risk_free_rate,
    strike_price,
    expiry,
    step_number):
    '''二叉树模型

    :param asset_spot_price : 当前资产价格
    :param volatility       : 波动率
    :param risk_free_rate   : 无风险利率
    :param strike_price     : 行权价
    :param expiry           : 到期时长
    :param step_number      : 步数

    :return : 资产价格树和期权价格树
    '''
    # 计算参数
    time_step = expiry / step_number # 步长
    discount_factor = math.exp(-risk_free_rate * time_step) # 折现因子
    temp1 = math.exp((risk_free_rate + math.pow(volatility, 2)) * time_step)
    temp2 = 0.5 * (discount_factor + temp1)
    u = temp2 + math.sqrt(math.pow(temp2, 2) - 1) # 上涨因子
    d = 1 / u # 下跌因子
    p = (math.exp(risk_free_rate * time_step) - d) / (u - d) # 上涨概率（风险中性概率）

    # 计算底层资产价格二叉树 ：从第一步往后推导
    asset_tree = [[asset_spot_price, ],]
    for n in range(1, step_number + 1) :
        lst = []
        for i in range(0, n) :
            # 价格=前一步对应位置的价格*上涨因子
            lst.append(asset_tree[n-1][i] * u)
        # 最下面一个节点的价格=前一步最下方价格*下跌因子
        lst.append(asset_tree[n-1][-1] * d)
        asset_tree.append(lst)

    # 计算期权价格二叉树：从最后一步倒推
    def _call_option_payoff(asset_spot_price, strike_price) :
        return 0 if asset_spot_price < strike_price else asset_spot_price - strike_price

    option_tree = [[] for _ in range(len(asset_tree)) ]
    # 计算终点的期权payoff
    last_step = asset_tree[-1]
    for asset_price in last_step :
        option_tree[-1].append(_call_option_payoff(asset_price, strike_price))

    # 倒推
    for n in range(len(option_tree) - 1, 0, -1) :
        next_step = option_tree[n]
        for i in range(len(next_step) - 1) :
            # 上涨和下跌两个分支的期望*折现因子
            v = (p * next_step[i] + (1 - p) * next_step[i + 1]) * discount_factor
            option_tree[n - 1].append(v)

    return {
        'price' : option_tree[0][0],
        'inter' : {
            'asset' : asset_tree,
            'option' : option_tree,
            'time_step' : time_step,
            'discount_factor' : discount_factor,
            'u' : u, 'd' : d, 'p' : p,
        },
        'param' : {
            'asset_spot_price' : asset_spot_price,
            'volatility'       : volatility      ,
            'risk_free_rate'   : risk_free_rate  ,
            'strike_price'     : strike_price    ,
            'expiry'           : expiry          ,
            'step_number'      : step_number     ,
        },
    }

def american_option_price_by_binomial_tree(
    asset_spot_price,
    volatility,
    risk_free_rate,
    strike_price,
    expiry,
    step_number):
    '''二叉树模型(允许提前行权)

    :param asset_spot_price : 当前资产价格
    :param volatility       : 波动率
    :param risk_free_rate   : 无风险利率
    :param strike_price     : 行权价
    :param expiry           : 到期时长
    :param step_number      : 步数

    :return : 资产价格树和期权价格树
    '''
    # 计算参数
    time_step = expiry / step_number # 步长
    discount_factor = math.exp(-risk_free_rate * time_step) # 折现因子
    temp1 = math.exp((risk_free_rate + math.pow(volatility, 2)) * time_step)
    temp2 = 0.5 * (discount_factor + temp1)
    u = temp2 + math.sqrt(math.pow(temp2, 2) - 1) # 上涨因子
    d = 1 / u # 下跌因子
    p = (math.exp(risk_free_rate * time_step) - d) / (u - d) # 上涨概率（风险中性概率）

    # 计算底层资产价格二叉树 ：从第一步往后推导
    asset_tree = [[asset_spot_price, ],]
    for n in range(1, step_number + 1) :
        lst = []
        for i in range(0, n) :
            # 价格=前一步对应位置的价格*上涨因子
            lst.append(asset_tree[n-1][i] * u)
        # 最下面一个节点的价格=前一步最下方价格*下跌因子
        lst.append(asset_tree[n-1][-1] * d)
        asset_tree.append(lst)

    # 计算期权价格二叉树：从最后一步倒推
    def _call_option_payoff(asset_spot_price, strike_price) :
        return 0 if asset_spot_price < strike_price else asset_spot_price - strike_price

    option_tree = [[] for _ in range(len(asset_tree)) ]
    # 计算终点的期权payoff
    last_step = asset_tree[-1]
    for asset_price in last_step :
        option_tree[-1].append(_call_option_payoff(asset_price, strike_price))

    # 倒推
    for n in range(len(option_tree) - 1, 0, -1) :
        next_step = option_tree[n]
        for i in range(len(next_step) - 1) :
            # 上涨和下跌两个分支的期望*折现因子
            v = (p * next_step[i] + (1 - p) * next_step[i + 1]) * discount_factor
            payoff = _call_option_payoff(asset_tree[n-1][i], strike_price)
            v = v if v > payoff else payoff # 如果期权payoff比价格高，选择提前行权获取更高收益
            option_tree[n - 1].append(v)

    return {
        'price' : option_tree[0][0],
        'inter' : {
            'asset' : asset_tree,
            'option' : option_tree,
            'time_step' : time_step,
            'discount_factor' : discount_factor,
            'u' : u, 'd' : d, 'p' : p,
        },
        'param' : {
            'asset_spot_price' : asset_spot_price,
            'volatility'       : volatility      ,
            'risk_free_rate'   : risk_free_rate  ,
            'strike_price'     : strike_price    ,
            'expiry'           : expiry          ,
            'step_number'      : step_number     ,
        },
    }

if __name__ == '__main__':
    def print_binomial_tree(lst):
        sep = ' ' * 4
        fmt = '{:6.2f}'
        prefix = ' ' * 5

        row_number = len(lst)
        for row_index, row in enumerate(lst) :
            print(prefix * (row_number - row_index), end='')
            for col_index, col in enumerate(row) :
                print(fmt.format(col), end=sep)
            print()

    result = option_price_by_binomial_tree(100., 0.2, 0.1, 100, 1/3, 4)
    print_binomial_tree(result['inter']['asset'])
    print_binomial_tree(result['inter']['option'])

    print(result)

    import matplotlib.pyplot as plt
    step_number_list = range(3, 253, 2)
    result_list = [option_price_by_binomial_tree(100., 0.2, 0.1, 100, 1/3, step_number)['price'] for step_number in step_number_list ]
    plt.scatter(step_number_list, result_list, label='odd steps')
    step_number_list = range(2, 253, 2)
    result_list = [option_price_by_binomial_tree(100., 0.2, 0.1, 100, 1/3, step_number)['price'] for step_number in step_number_list ]
    plt.scatter(step_number_list, result_list, label='even steps')
    plt.legend()
    plt.show()

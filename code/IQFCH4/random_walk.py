# -*- coding: utf-8 -*-

# @date   : 2020-05-28
# @author : Guo Peng
# @brief  : 随机游走

import math
import random

def random_walk(asset, drift, volatility, timestep, step_number) :
    '''随机游走'''
    def _rand(avg = 6) :
        '''生成随机数'''
        times = int(avg * 2)
        r = 0
        for _ in range(times) :
            r += random.randint(1, 10000) / 10000 # 产生均匀分布随机数
        r -= times / 2
        return r

    lst = [asset, ]
    for _ in range(step_number - 1) :
        r = _rand()
        # 随机游走模型
        v = lst[-1] * (1 + drift * timestep + volatility * math.sqrt(timestep) * r)
        lst.append(v)

    return lst

if __name__ == '__main__' :
    import matplotlib.pyplot as plt
    import pandas as pd

    # price
    lst = random_walk(100, 0.15, 0.25, 0.01, 1000)

    # return
    n = pd.Series(lst)
    ns = n.shift(1)
    r = (n - ns) / ns

    fig, ax = plt.subplots(3, 1)

    fig.suptitle('random walk')

    ax[0].set_title('price')
    ax[0].plot(lst)

    ax[1].set_title('price histgram')
    ax[1].hist(lst)

    ax[2].set_title('return histgram')
    ax[2].hist(r)

    fig.show()
    plt.show()

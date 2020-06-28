# -*- coding: utf-8 -*-

# @date   : 2020-06-27
# @author : Guo Peng
# @brief  : option pricing by binomial tree

import os
import xlrd
import math
import pandas as pd
from scipy.stats import norm

#os.chdir('M1/L1')

# load adjust close from excel file
data = xlrd.open_workbook('CQF_June_2020_M1L1_Excel.xlsx')
table = data.sheets()[0]

date = table.col_values(0, 1, None)
adj_close = table.col_values(5, 1, None)

# return
adj_close = pd.Series(adj_close, index=date)
adj_close_shift = adj_close.shift(1)
returns = (adj_close - adj_close_shift) / adj_close_shift
returns.dropna(inplace=True) # drop nan

# scale return
mean = returns.mean()
std = returns.std()
scaled_returns = (returns - mean) / std

# returns distribution
# stat
minimum = scaled_returns.min()
maximum = scaled_returns.max()
count = len(scaled_returns)

# cut and count
bucket_num = 200
bucket_width = (maximum - minimum) / bucket_num
end_pt = pd.Series([minimum + i * bucket_width for i in range(bucket_num+1)])
c = pd.cut(scaled_returns, end_pt) # split
c = scaled_returns.groupby(c).agg(['count'])['count'] # group count
freq = pd.Series(c)
# probability density function
pdf = freq / count / bucket_width

# pdf for z-distribution
mid_pt = end_pt - 0.5 * bucket_width
pdf_z_dist = mid_pt.apply(lambda x: math.exp(-0.5*x*x) / math.sqrt(2 * math.pi))

# align for plot
end_pt = end_pt[:bucket_num]
pdf_z_dist = pdf_z_dist[:bucket_num]

# plot
import matplotlib.pyplot as plt

def _plot(ax, x, y, label, *args, **kwargs) :
    ax.plot(x, y, label=label)

def _plots(ax, lst, fontsize=12) :
    for item in lst :
        _plot(ax, **item)
    ax.legend(fontsize=fontsize)
    [label.set_fontsize(fontsize) for label in ax.get_xticklabels() + ax.get_yticklabels()]
    ax.grid()



# relationship between mean/standard deviation and δt
def delta_t(adj_close, t) :
    s = adj_close[::t]
    #print(s)
    adj_close_shift = s.shift(1)
    returns = (adj_close - adj_close_shift) / adj_close_shift
    returns.dropna(inplace=True) # drop nan

    # scale return
    mean = returns.mean()
    std = returns.std()
    return t, mean, std

s = [delta_t(adj_close, t) for t in range(1, 180) ]

t = pd.Series([x[0] for x in s])
mean = pd.Series([x[1] for x in s])
std = pd.Series([x[2] for x in s])

fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 8))
_plots(axes[0], [{'x' : t, 'y' : mean, 'label' : 'mean', },
    {'x' : t, 'y' : mean.rolling(20).mean(), 'label' : 'mean.ma', },])
_plots(axes[1], [{'x' : t, 'y' : std, 'label' : 'std', },
    {'x' : t, 'y' : std.rolling(20).mean(), 'label' : 'std.ma', },])
fig.savefig('./delta_t.svg', format='svg')



# robust of μ&σ

s = [delta_t(adj_close, t) for t in range(1, 180) ]

t = [x[0] for x in s]
mu_list = [x[1] / (x[0] / 252) for x in s ]
sigma_list = [x[2] / math.sqrt(x[0] / 252) for x in s ]

fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 8))
_plots(axes[0], [{'x' : t, 'y' : mu_list, 'label' : 'mu', },])
_plots(axes[1], [{'x' : t, 'y' : sigma_list, 'label' : 'sigma', }, ])
fig.savefig('./mu_sigma.svg', format='svg')


# Returns distribution and normal distribution
# quantile for returns
quantile_returns = scaled_returns.sort_values()

# quantile for z-distribution
cum_z_dist = pd.Series(range(0, count)) / count
quantile_z_dist = cum_z_dist.apply(lambda x : norm.ppf(x,loc=0,scale=1))

fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))
_plots(axes, [{'x' : end_pt, 'y' : pdf, 'label' : 'returns distrbute', },
    {'x' : end_pt, 'y' : pdf_z_dist, 'label' : 'z distrbute', },])
fig.savefig('./distribute.svg', format='svg')



# qq plot
fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))
_plots(axes, [{'x' : quantile_z_dist, 'y' : quantile_returns, 'label' : ' ', },])
fig.savefig('./qq_plot.svg', format='svg')



plt.show()


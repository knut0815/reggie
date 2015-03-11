"""
Plotting for various models.
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import numpy as np
import matplotlib.pyplot as pl

__all__ = ['plot_posterior']


def _figure(fig, draw=True):
    if draw:
        fig.canvas.draw()
    return fig


def _axis(ax, legend=True, despine=True, draw=True):
    ax.axis('tight')
    if despine:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    if legend:
        ax.legend(loc=0)
    if draw:
        ax.figure.canvas.draw()
    return ax


def plot_posterior(model, xmin=None, xmax=None, data=True, predictive=False,
                   **kwargs):
    """
    Plot the marginal distribution of the given one-dimensional posterior
    model.
    """

    # if not isinstance(model, PosteriorModel):
    #     raise ValueError('model must be a PosteriorModel instance')

    if model.ndata == 0 and (xmin is None or xmax is None):
        raise ValueError('model has no data and no bounds are given')

    # grab the data
    X, Y = model.data

    # get the input points
    xmin = np.min(X) if (xmin is None) else xmin
    xmax = np.max(X) if (xmax is None) else xmax
    x = np.linspace(xmin, xmax, 500)

    # get the posterior mean and confidence bands
    mu, s2 = model.get_posterior(x[:, None], predictive=predictive)
    lo = mu - 2 * np.sqrt(s2)
    hi = mu + 2 * np.sqrt(s2)

    # get the axes.
    lw = 2
    ls = '-'
    alpha = 0.25

    # get the axis
    ax = pl.gca()
    ax.cla()

    # plot the mean
    lines = ax.plot(x, mu, lw=lw, ls=ls, label='mean')
    color = lines[0].get_color()

    # plot error bars
    ax.fill_between(x, lo, hi, color=color, alpha=alpha)
    ax.plot([], [], lw=10, color=color, alpha=alpha, label='uncertainty')

    if data:
        ax.scatter(X.ravel(), Y, zorder=5, marker='o', s=30, lw=1,
                   facecolors='none', label='data')

    # complete the axis
    _axis(ax, **kwargs)


def plot_chain(samples, names=None, **kwargs):
    samples = samples - np.min(samples, axis=0)
    samples /= np.max(samples, axis=0)

    d = samples.shape[1]

    fig = pl.gcf()
    fig.clf()
    draw = kwargs.pop('draw', True)

    for i in xrange(d):
        ax = fig.add_subplot(d, 1, i+1)
        ax.plot(samples[:, i])
        ax.set_yticklabels([])
        if names is not None:
            ax.set_ylabel(names[i])
        if i < d-1:
            ax.set_xticklabels([])
        ax = _axis(ax, draw=False, **kwargs)

    # complete the figure
    _figure(fig, draw)


def plot_pairs(samples, names=None, **kwargs):
    fig = pl.gcf()
    fig.clf()

    draw = kwargs.pop('draw', True)
    legend = kwargs.pop('legend', True)

    d = samples.shape[1]

    for i, j in np.ndindex(d, d):
        if i >= j:
            continue
        ax = fig.add_subplot(d-1, d-1, (j-1)*(d-1)+i+1)
        ax.scatter(samples[:, i], samples[:, j], edgecolor='white', alpha=0.1)

        # get rid of the internal labels
        if i > 0:
            ax.set_yticklabels([])
        if j < d-1:
            ax.set_xticklabels([])

        # set the labels
        if i == 0 and names is not None:
            ax.set_ylabel(names[j])
        if j == d-1 and names is not None:
            ax.set_xlabel(names[i])

        _axis(ax, draw=False, **kwargs)

    # complete the figure
    _figure(fig, draw)

"""
Implementation of the matern kernel.
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import numpy as np

from .kernel import RealKernel
from ._distances import rescale, dist, dist_foreach, diff
from ..core.domains import POSITIVE

__all__ = ['Matern']


class Matern(RealKernel):
    def __init__(self, rho, ell, d=3, ndim=None):
        if d not in {1, 3, 5}:
            raise ValueError('d must be one of 1, 3, or 5')

        # get the shape that ell should be
        shape = ('d',) if (ndim is None) else ()

        # register our parameters
        self._rho = self._register('rho', rho, domain=POSITIVE)
        self._ell = self._register('ell', ell, domain=POSITIVE, shape=shape)

        # save flags for iso/ndim
        self._d = d
        self._iso = ndim is not None
        self.ndim = ndim if self._iso else self._ell.size

    def __repr__(self):
        kwargs = {}
        if self._iso:
            kwargs['ndim'] = self.ndim
        if self._d != 3:
            kwargs['d'] = self._d
        return super(Matern, self).__repr__(**kwargs)

    def _f(self, r):
        return (
            1 if (self._d == 1) else
            1+r if (self._d == 3) else
            1+r*(1+r/3.))

    def _g(self, r):
        return (
            1 if (self._d == 1) else
            r if (self._d == 3) else
            r*(1+r)/3.)

    def get_kernel(self, X1, X2=None):
        X1, X2 = rescale(self._ell, X1, X2)
        D = dist(X1, X2, metric='euclidean')
        K = self._rho * np.exp(-D) * self._f(D)
        return K

    def get_dkernel(self, X1):
        return np.full(len(X1), self._rho)

    def get_grad(self, X1, X2=None):
        X1, X2 = rescale(self._ell, X1, X2)
        D = dist(X1, X2, metric='euclidean')
        E = np.exp(-D)
        S = E * self._f(D)
        M = self._rho * E * self._g(D)

        yield S                                     # derivative wrt rho
        if self._iso:
            yield M * D / self._ell                 # derivative wrt ell (iso)
        else:
            for i, D_ in enumerate(dist_foreach(X1, X2)):
                with np.errstate(invalid='ignore'):
                    G = M * D_ / D / self._ell[i]   # derivative wrt ell (ard)
                    yield np.where(D < 1e-12, 0, G)

    def get_dgrad(self, X1):
        yield np.ones(len(X1))
        for _ in xrange(self.nparams-1):
            yield np.zeros(len(X1))

    def get_gradx(self, X1, X2=None):
        X1, X2 = rescale(self._ell, X1, X2)
        D1 = diff(X1, X2)
        D = np.sqrt(np.sum(D1**2, axis=-1))
        S = self._rho * np.exp(-D)
        with np.errstate(invalid='ignore'):
            M = np.where(D < 1e-12, 0, S * self._g(D) / D)
        G = -M[:, :, None] * D1 / self._ell
        return G
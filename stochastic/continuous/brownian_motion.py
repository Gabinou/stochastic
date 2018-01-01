"""Brownian motion and derivative processes."""
import numpy as np

from stochastic.noise.gaussian_noise import GaussianNoise


class BrownianMotion(GaussianNoise):
    """Brownian motion.

    A standard Brownian motion (discretely sampled) has independent and
    identically distributed Gaussian increments with variance equal to
    increment length. Non-standard Brownian motion includes a linear drift
    parameter and scale factor.

    :param float t: the right hand endpoint of the time interval :math:`[0,t]`
        for the process
    :param float drift: rate of change of the expected value
    :param float scale: scale factor of the Gaussian process
    """

    def __init__(self, t=1, drift=0, scale=1):
        super().__init__(t)
        self.drift = drift
        self.scale = scale

    def __str__(self):
        if self.drift == 0 and self.scale == 1:
            s = "Standard Brownian motion on interval [0, {t}]".format(
                t=self.t)
            return s
        s = ("Brownian motion with drift {d} and scale {s} on interval "
             "[0, {t}].")
        return s.format(
            t=str(self.t),
            d=str(self.drift),
            s=str(self.scale)
        )

    def __repr__(self):
        if self.drift == 0 and self.scale == 1:
            return "BrownianMotion(t={t})".format(t=self.t)
        return "BrownianMotion(t={t}, drift={d}, scale={s})".format(
            t=str(self.t),
            d=str(self.drift),
            s=str(self.scale)
        )

    @property
    def drift(self):
        """Drift parameter."""
        return self._drift

    @drift.setter
    def drift(self, value):
        self._check_number(value, "Drift")
        self._drift = value

    @property
    def scale(self):
        """Scale parameter."""
        return self._scale

    @scale.setter
    def scale(self, value):
        self._check_positive_number(value, "Scale")
        self._scale = value

    def _sample_brownian_motion(self, n, zero=True):
        """Generate a realization of Brownian Motion.

        Generate a Brownian motion realization with n increments. If zero is
        True then include W_0 = 0.
        """
        self._check_zero(zero)

        line = self._linspace(self.drift, n, zero)
        bm = np.cumsum(self.scale * self._sample_gaussian_noise(n, zero))

        return line + bm

    def sample(self, n, zero=True):
        """Generate a realization.

        :param int n: the number of increments to generate
        :param bool zero: if True, include :math:`t=0`
        """
        return self._sample_brownian_motion(n, zero)

    def _sample_brownian_motion_at(self, times, zero=True):
        """Generate a Brownian motion at specified times."""
        return np.cumsum(self._sample_gaussian_noise_at(times, zero))

    def sample_at(self, times, zero=True):
        """Generate a realization using specified times.

        :param times: a vector of increasing time values at which to generate
            the realization
        :param bool zero: if True, include :math:`t=0`
        """
        return self._sample_brownian_motion_at(times)

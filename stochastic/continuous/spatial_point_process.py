"""Spatial Point Processes."""

from stochastic.continuous.poisson import PoissonProcess
import inspect
import numpy as np
import scipy

class SpatialPointProcess(PoissonProcess):
    r"""Spatial Point Process.

    .. image:: _static/mixed_poisson_process.png
        :scale: 50%

    A mixed poisson process is a Poisson process for which the rate is
    a scalar random variate. The sample method will generate a random variate
    for the rate before generating a Poisson process realization with the rate.
    A Poisson process with rate :math:`\lambda`
    is a count of occurrences of i.i.d. exponential random
    variables with mean :math:`1/\lambda`. Use the ``rate`` attribute to get
    the most recently generated random rate.

    :param callable density: either a callable or n-dimensional array. Note:
    Only a single positional argument is assumed, a n-dimensinoal array.
    :param tuple bounds: Bounds in wihch to simulate samples. The number of 
    bound pairs must be the same as input arguments of callable density or 
    number of the density array.
    :param dict density_kwargs: keyword args for callable ``density``
    """

    def __init__(self, density, density_kwargs={}):
        self.density = density
        self.density_kwargs = density_kwargs

    def __str__(self):
        return "Spatial point process with specified density function in multidimensional space."

    def __repr__(self):
        return "MixedPoissonProcess(" \
            "density={d}, density_kwargs={dkw})".format(
                rf=str(self.density),
                rkw=str(self.density_kwargs)
            )

    @property
    def density(self):
        """Probability density in the data space."""
        return self._density

    @density.setter
    def density(self, value):
        if (not callable(value)) & (not isinstance(value, (list, tuple, np.ndarray))):
            raise ValueError("Density must be a callable or n-dimensional array.")
        self._density = value

    @property
    def density_kwargs(self):
        """Keyword arguments for the density function."""
        return self._density_kwargs

    @density_kwargs.setter
    def density_kwargs(self, value):
        if not isinstance(value, dict):
            raise ValueError("Density kwargs must be a dict.")
        self._density_kwargs = value

    def _sample_spatial_point_process(self, n=None, bounds=(), algo='thinning', blocksize=1000):
        if (n is not None) & (bounds is not ()):
            if algo=='thinning':

                if callable(self.density):
                    boundstuple=[]
                    for i in bounds: boundstuple+=(tuple(i),)
                    max = scipy.optimize.minimize(lambda x: -self.density(x),x0=[np.mean(i) for i in bounds],bounds = boundstuple)
                    lmax = self.density(max.x, *self.density_kwargs)
                else:
                    lmax = np.amax(self.density)

                Thinned = np.array([])
                while len(Thinned.T) < n:
                    if callable(self.density):
                        for bound in bounds:
                            if 'Unthinned' not in locals():
                                Unthinned = np.random.uniform(*bound, size=(blocksize))
                            else:
                                Unthinned = np.vstack((Unthinned, np.random.uniform(*bound, size=(blocksize))))
                    else:
                        for shape in self.density.shape:
                            if 'Unthinned' not in locals():
                                Unthinned = np.random.randint(0, shape, size=(blocksize))
                            else:
                                Unthinned = np.vstack((Unthinned, np.random.randint(0, shape, size=(blocksize))))
                    if len(Unthinned.T.shape)==1:
                        Unthinned.T = np.reshape(Unthinned, (1, len(Unthinned)))
                    U = np.random.uniform(size=(blocksize))
                    if callable(self.density): 
                        Criteria = self.density(Unthinned.T)/lmax
                    else:
                        Criteria_ndim = self.density/lmax
                        Criteria = []
                        for point in Unthinned.T:
                            Criteria.append(Criteria_ndim[tuple(point)])
                    if len(Thinned) == 0:
                        Thinned = Unthinned[:, U < Criteria]
                    else:
                        Thinned = np.hstack((Thinned, Unthinned[:, U < Criteria]))
                    del Unthinned
                Thinned = Thinned[:, :n]
                return(Thinned.T)

    def sample(self, n=None, bounds=(), algo='thinning', blocksize=1000):
        """Generate a realization.

        The number of samples ``n`` and the spatial ``bounds`` must be provided.
        The number of dimensions is taken to be the number of bound pairs in    
        ``bounds``

        :param int n: the number of arrivals to simulate
        :param tuple bounds: the bounds in which to generate arrivals
        :param str algo: the general algorithm
        """
        print('a')
        if callable(self.density):
            try:
                print(*bounds)
                self.density(*bounds, **self.density_kwargs)
            except:
                pass
        return self._sample_spatial_point_process(n, bounds, algo, blocksize)

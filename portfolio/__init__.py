# Make key functions available at package level if desired
from .data import get_returns, get_volatilities, covariance_matrix, compute_benchmark
from .optim import portfolios
from .plotting import graph

__all__ = [
    "get_returns", "get_volatilities", "covariance_matrix", "compute_benchmark",
    "portfolios", "graph"
]

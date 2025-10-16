import numpy as np
from .data import get_returns, covariance_matrix


def portfolios(tickers, wanted_return, wanted_volatility, rf):
    return_vector = np.array(get_returns(tickers)).reshape(-1, 1)
    sigma_matrix = covariance_matrix(tickers)

    ones = np.ones((len(return_vector), 1))

    inv_sigma = np.linalg.inv(sigma_matrix)
    A = (ones.T @ inv_sigma @ ones).item()
    B = (ones.T @ inv_sigma @ return_vector).item()
    C = (return_vector.T @ inv_sigma @ return_vector).item()
    DELTA = (A * C - B ** 2)

    minimum_variance_portfolio = (inv_sigma @ ones) / A
    second_portfolio = (inv_sigma @ return_vector) / B

    return_minumim_variance_portfolio = (minimum_variance_portfolio.T @ return_vector).item()
    sd_minimum_variance_portfolio = (np.sqrt((A * (return_minumim_variance_portfolio ** 2) - 2 * B * return_minumim_variance_portfolio + C) / DELTA)).item()
    sharpe_minimum_variance_portfolio = (return_minumim_variance_portfolio - rf) / sd_minimum_variance_portfolio

    # choose target r with/without rf based on inputs
    if wanted_return == "blank":
        if wanted_volatility is None:
            raise ValueError("Provide either desired return μ or desired volatility σ.")
        if wanted_volatility < sd_minimum_variance_portfolio:
            r_for_no_rf = return_minumim_variance_portfolio
        else:
            disc = (4 * B ** 2 - 4 * A * (C - DELTA * wanted_volatility ** 2))
            if disc < 0:
                raise ValueError("Desired σ not attainable by the frontier (discriminant < 0).")
            r_for_no_rf = max(
                (2 * B + np.sqrt(disc)) / (2 * A),
                (2 * B - np.sqrt(disc)) / (2 * A),
            )
        r_with_rf = max(wanted_volatility * np.sqrt(C - 2 * rf * B + (rf ** 2) * A) + rf,
                        -(wanted_volatility * np.sqrt(C - 2 * rf * B + (rf ** 2) * A)) + rf)
    else:
        # target μ provided
        if wanted_return < return_minumim_variance_portfolio:
            r_for_no_rf = return_minumim_variance_portfolio
        else:
            r_for_no_rf = wanted_return
        r_with_rf = wanted_return

    # No risk-free asset
    optimal_portfolio = (((C - r_for_no_rf * B) * A) / DELTA) * minimum_variance_portfolio + (((r_for_no_rf * A - B) * B) / DELTA) * second_portfolio
    sd_optimal_portfolio = np.sqrt((A * (r_for_no_rf ** 2) - 2 * B * r_for_no_rf + C) / DELTA).item()
    sharpe_optimal = (r_for_no_rf - rf) / sd_optimal_portfolio

    r = np.linspace(0, max(get_returns(tickers)) + 0.1, 1000)
    sd_general = np.sqrt((A * (r ** 2) - 2 * B * r + C) / DELTA)

    # Risk-free asset
    tangent_portfolio = (inv_sigma @ (return_vector - rf * ones)) / (B - rf * A)
    return_tangent_portfolio = (tangent_portfolio.T @ return_vector).item()
    sd_tangent_portfolio = (np.sqrt((A * (return_tangent_portfolio ** 2) - 2 * B * return_tangent_portfolio + C) / DELTA)).item()
    sharpe_tangent = (return_tangent_portfolio - rf) / sd_tangent_portfolio

    lagrangian_multiplier_riskless = (r_with_rf - rf) / (C - 2 * rf * B + (rf ** 2) * A)

    optimal_portfolio_w_rf_riskyweights = lagrangian_multiplier_riskless * (B - rf * A) * tangent_portfolio
    optimal_portfolio_w_rf_leverage = 1 - optimal_portfolio_w_rf_riskyweights.T @ ones

    sd_optimal_portfolio_w_riskless = (abs(r_with_rf - rf)) / np.sqrt(C - 2 * rf * B + (rf ** 2) * A).item()

    sd_general_for_w_riskfree = (abs(r - rf)) / np.sqrt(C - 2 * rf * B + (rf ** 2) * A)

    # pack everything (preserve your original ordering for compatibility with the template)
    everything = [
        minimum_variance_portfolio, return_minumim_variance_portfolio, sd_minimum_variance_portfolio,
        optimal_portfolio, sd_optimal_portfolio,
        r, sd_general,
        tangent_portfolio, return_tangent_portfolio, sd_tangent_portfolio,
        optimal_portfolio_w_rf_riskyweights, optimal_portfolio_w_rf_leverage, sd_optimal_portfolio_w_riskless,
        sd_general_for_w_riskfree,
        r_for_no_rf, r_with_rf,
        sharpe_minimum_variance_portfolio, sharpe_optimal, sharpe_tangent
    ]
    return everything
